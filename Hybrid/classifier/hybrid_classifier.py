"""
hybrid_classifier.py
--------------------
Plan A+B: combine local semantic similarity with LLM API calls to get
the best balance of accuracy and cost.

Decision logic
--------------
                ┌─────────────────────────────────────────────────────┐
                │  semantic_score >= HYBRID_HIGH_THRESHOLD            │
                │  → Accept as relevant immediately (no API call)     │
                ├─────────────────────────────────────────────────────┤
                │  semantic_score < SEMANTIC_THRESHOLD                │
                │  → Reject as irrelevant immediately (no API call)   │
                ├─────────────────────────────────────────────────────┤
                │  SEMANTIC_THRESHOLD <= score < HYBRID_HIGH_THRESHOLD│
                │  → "Uncertain zone": send to LLM for final verdict  │
                └─────────────────────────────────────────────────────┘

In practice, only 10–25 % of comments fall in the uncertain zone,
so the API call volume (and cost) is kept small.
"""

import pandas as pd
from typing import List

from kiruna_classifier import config
from kiruna_classifier import semantic_classifier
from kiruna_classifier import llm_classifier


def classify(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the full hybrid classification pipeline on a cleaned DataFrame.

    Parameters
    ----------
    df : cleaned DataFrame with a CONTENT column

    Returns
    -------
    DataFrame with Kiruna_Related, Kiruna_Topic, Kiruna_Score, Semantic_Score,
    and LLM_Reason columns populated for every row.
    """
    low_thresh  = config.SEMANTIC_THRESHOLD
    high_thresh = config.HYBRID_HIGH_THRESHOLD
    api_key     = config.ANTHROPIC_API_KEY

    # ── Step 1: semantic pre-scoring ───────────────────────────────────────
    print("\n[Hybrid] Step 1/2 — Semantic pre-scoring…")

    texts   = df["CONTENT"].tolist()
    results = semantic_classifier.score_texts(texts)

    df = df.copy()
    df["Semantic_Score"] = [r[0] for r in results]
    df["Semantic_Topic"] = [r[1] for r in results]

    # Partition rows into three confidence buckets
    high_conf_rel: List[int] = df.index[df["Semantic_Score"] >= high_thresh].tolist()
    high_conf_irr: List[int] = df.index[df["Semantic_Score"] <  low_thresh].tolist()
    uncertain:     List[int] = df.index[
        (df["Semantic_Score"] >= low_thresh) &
        (df["Semantic_Score"] <  high_thresh)
    ].tolist()

    print(
        f"[Hybrid]  Confident relevant : {len(high_conf_rel)}\n"
        f"[Hybrid]  Confident irrelevant: {len(high_conf_irr)}\n"
        f"[Hybrid]  Uncertain (→ LLM)  : {len(uncertain)}"
    )

    # Initialise output columns
    for col in ["Kiruna_Related", "Kiruna_Topic", "Kiruna_Score", "LLM_Reason"]:
        df[col] = "" if col != "Kiruna_Score" else 0

    # Apply semantic verdict directly for high-confidence buckets
    for idx in high_conf_rel:
        topic = df.at[idx, "Semantic_Topic"]
        df.at[idx, "Kiruna_Related"] = "Yes"
        df.at[idx, "Kiruna_Topic"]   = topic
        df.at[idx, "Kiruna_Score"]   = config.TOPIC_SCORE_MAP.get(topic, 0)

    for idx in high_conf_irr:
        df.at[idx, "Kiruna_Related"] = "No"
        df.at[idx, "Kiruna_Topic"]   = "Irrelevant"
        df.at[idx, "Kiruna_Score"]   = 0

    # ── Step 2: LLM refinement for uncertain cases ─────────────────────────
    if not uncertain:
        print("[Hybrid] No uncertain cases — skipping LLM step.")
        return df

    if api_key == "YOUR_API_KEY_HERE":
        # No API key provided: fall back to accepting the semantic verdict
        print(
            "[Hybrid] ANTHROPIC_API_KEY not set. "
            "Uncertain rows will use semantic verdict as fallback."
        )
        for idx in uncertain:
            topic = df.at[idx, "Semantic_Topic"]
            df.at[idx, "Kiruna_Related"] = "Yes"
            df.at[idx, "Kiruna_Topic"]   = topic
            df.at[idx, "Kiruna_Score"]   = config.TOPIC_SCORE_MAP.get(topic, 0)
        return df

    print("\n[Hybrid] Step 2/2 — LLM refinement of uncertain cases…")
    df = llm_classifier.classify(df, indices=uncertain)

    return df
