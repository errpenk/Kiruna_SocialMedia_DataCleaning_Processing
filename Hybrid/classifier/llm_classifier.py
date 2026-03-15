"""
llm_classifier.py
-----------------
Plan B: classify comments by calling the Anthropic Claude API.

Each batch of comments is sent in a single API request with a structured
system prompt. Claude returns a JSON array with one object per comment,
containing the topic label, a relevance flag, and a short reasoning string.

Advantages over keyword matching
---------------------------------
- Understands context, irony, and implicit references
- Handles all languages without language-specific rules
- Produces a human-readable reason for every classification decision
- Gracefully degrades on ambiguous cases instead of silently misfiring

Dependencies
------------
    pip install anthropic tqdm
"""

import json
import re
import time
import pandas as pd
from typing import Dict, List, Optional
from tqdm import tqdm

from kiruna_classifier import config


# ---------------------------------------------------------------------------
# System prompt sent to Claude for every batch
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are an expert research assistant helping classify Reddit comments
for an academic study about Kiruna, Sweden — specifically its urban relocation project,
mining industry (LKAB), Sami indigenous culture, and Arctic environment.

For each numbered comment below, output ONLY a valid JSON array (no markdown fences,
no explanation text outside the array). The array must have exactly one object per comment.

Each object must have exactly these three keys:
  "related" : boolean  — true if the comment is relevant to Kiruna or its relocation context
  "topic"   : string   — one of the following labels (pick the single best fit):
                "Church/City Relocation"
                "Mining/Industry"
                "Aerospace"
                "Sami Culture"
                "Climate/Nature"
                "Place Name"
                "Tourism/Activities"
                "Nordic Life/Culture"
                "Irrelevant"
  "reason"  : string   — one concise sentence explaining the classification (max 15 words)

Classification rules:
- A tangential mention of Sweden or the Arctic without clear Kiruna context → Irrelevant
- City relocation, church demolition, or LKAB mine subsidance → Church/City Relocation (score 5)
- An emotional reaction ("wow", "cool") that is clearly responding to Kiruna content → Place Name
- Comments in Swedish, Finnish, or any other language: judge the meaning, not the language
- When in doubt between two topics, pick the more specific one
"""


# ---------------------------------------------------------------------------
# API call (single batch)
# ---------------------------------------------------------------------------

def _call_api(batch_texts: List[str]) -> List[Dict]:
    """
    Send one batch of texts to Claude and return the parsed JSON result list.

    Retries up to LLM_MAX_RETRIES times with exponential backoff on failure.
    Falls back to a list of Irrelevant dicts if all retries are exhausted.
    """
    import anthropic

    client   = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(batch_texts))
    user_msg = f"Classify these {len(batch_texts)} Reddit comments:\n\n{numbered}"

    for attempt in range(1, config.LLM_MAX_RETRIES + 1):
        try:
            response = client.messages.create(
                model=config.LLM_MODEL,
                max_tokens=config.LLM_MAX_TOKENS,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()

            # Strip any accidental markdown code fences the model may have added
            raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()

            parsed = json.loads(raw)

            # Sanity check: the array must have exactly one entry per input
            if len(parsed) == len(batch_texts):
                return parsed

            print(
                f"[LLM] Warning: expected {len(batch_texts)} items, "
                f"got {len(parsed)}. Retrying…"
            )

        except Exception as exc:
            print(f"[LLM] Attempt {attempt}/{config.LLM_MAX_RETRIES} failed: {exc}")
            if attempt < config.LLM_MAX_RETRIES:
                time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s

    # All retries exhausted — return a safe fallback so the pipeline continues
    print("[LLM] All retries failed. Marking batch as Irrelevant.")
    return [
        {"related": False, "topic": "Irrelevant", "reason": "API error — fallback"}
    ] * len(batch_texts)


# ---------------------------------------------------------------------------
# DataFrame-level classification
# ---------------------------------------------------------------------------

def classify(
    df: pd.DataFrame,
    indices: Optional[List[int]] = None,
) -> pd.DataFrame:
    """
    Classify comments using the Claude API and write results back into df.

    Parameters
    ----------
    df      : DataFrame with a CONTENT column (index must be intact).
    indices : Optional list of integer positional indices to classify.
              If None, all rows are classified.

    Returns
    -------
    The same DataFrame with Kiruna_Related, Kiruna_Topic, Kiruna_Score,
    and LLM_Reason columns populated for the targeted rows.
    """
    if indices is None:
        indices = list(range(len(df)))

    print(
        f"\n[LLM] Classifying {len(indices)} comments "
        f"(model={config.LLM_MODEL}, batch_size={config.LLM_BATCH_SIZE})…"
    )

    # Initialise output columns if they do not exist yet
    for col in ["Kiruna_Related", "Kiruna_Topic", "Kiruna_Score", "LLM_Reason"]:
        if col not in df.columns:
            df[col] = ""

    batch_size = config.LLM_BATCH_SIZE

    for start in tqdm(range(0, len(indices), batch_size), desc="LLM batches"):
        batch_idx   = indices[start : start + batch_size]
        batch_texts = df.loc[batch_idx, "CONTENT"].tolist()
        results     = _call_api(batch_texts)

        for row_idx, res in zip(batch_idx, results):
            topic   = res.get("topic",   "Irrelevant")
            related = res.get("related", False)

            df.at[row_idx, "Kiruna_Related"] = "Yes" if related else "No"
            df.at[row_idx, "Kiruna_Topic"]   = topic
            df.at[row_idx, "Kiruna_Score"]   = config.TOPIC_SCORE_MAP.get(topic, 0)
            df.at[row_idx, "LLM_Reason"]     = res.get("reason", "")

        # Respect API rate limits between batches
        time.sleep(config.LLM_SLEEP_BETWEEN_BATCHES)

    return df
