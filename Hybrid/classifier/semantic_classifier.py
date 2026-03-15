"""
semantic_classifier.py
-----------------------
Plan A: classify comments using cosine similarity against topic anchor phrases.

How it works
------------
1. A multilingual sentence-transformer model encodes each comment and each
   anchor phrase into a dense vector (embedding).
2. Cosine similarity is computed between every comment and every anchor.
3. The anchor with the highest similarity determines the topic label.
4. If the best similarity score is below SEMANTIC_THRESHOLD the comment is
   marked Irrelevant; otherwise it is marked as related to that topic.

No keyword lists are required. The model captures semantic meaning, so
synonyms, paraphrases, and other languages (Swedish, Finnish, etc.) are
handled automatically.

Dependencies
------------
    pip install sentence-transformers
"""

import numpy as np
import pandas as pd
from typing import List, Tuple

from kiruna_classifier import config


# ---------------------------------------------------------------------------
# Module-level model cache (lazy-loaded on first use)
# ---------------------------------------------------------------------------
_model = None


def _get_model():
    """
    Return the cached SentenceTransformer model, loading it on first call.
    The model file is downloaded once and then stored in the local cache.
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[Semantic] Loading model '{config.SEMANTIC_MODEL}' (downloaded on first run)…")
        _model = SentenceTransformer(config.SEMANTIC_MODEL)
    return _model


# ---------------------------------------------------------------------------
# Core similarity computation
# ---------------------------------------------------------------------------

def score_texts(texts: List[str]) -> List[Tuple[float, str]]:
    """
    Compute the best anchor similarity for each text.

    Parameters
    ----------
    texts : list of raw comment strings

    Returns
    -------
    List of (best_cosine_score, topic_label) tuples, one per input text.
    """
    from sentence_transformers import util

    model = _get_model()

    # Encode anchor phrases — these stay fixed for the whole run
    anchor_embeddings = model.encode(
        config.SEMANTIC_ANCHORS,
        convert_to_tensor=True,
        show_progress_bar=False,
    )

    # Encode all comment texts in one batched call for efficiency
    text_embeddings = model.encode(
        texts,
        convert_to_tensor=True,
        show_progress_bar=True,
    )

    # Cosine similarity matrix: shape (num_texts, num_anchors)
    cos_scores = util.cos_sim(text_embeddings, anchor_embeddings).cpu().numpy()

    results: List[Tuple[float, str]] = []
    for row in cos_scores:
        best_idx   = int(np.argmax(row))
        best_score = float(row[best_idx])
        best_topic = config.ANCHOR_TOPIC_MAP[best_idx]
        results.append((best_score, best_topic))

    return results


# ---------------------------------------------------------------------------
# DataFrame-level classification
# ---------------------------------------------------------------------------

def classify(df: pd.DataFrame, threshold: float | None = None) -> pd.DataFrame:
    """
    Add Kiruna_Related, Kiruna_Topic, Kiruna_Score, and Semantic_Score columns
    to the DataFrame using purely local semantic similarity.

    Parameters
    ----------
    df        : cleaned DataFrame with a CONTENT column
    threshold : override config.SEMANTIC_THRESHOLD for this call
    """
    if threshold is None:
        threshold = config.SEMANTIC_THRESHOLD

    print(f"\n[Semantic] Classifying {len(df)} comments (threshold={threshold})…")

    texts   = df["CONTENT"].tolist()
    results = score_texts(texts)

    df = df.copy()
    df["Semantic_Score"] = [r[0] for r in results]
    df["Kiruna_Related"] = [
        "Yes" if r[0] >= threshold else "No" for r in results
    ]
    df["Kiruna_Topic"] = [
        r[1] if r[0] >= threshold else "Irrelevant" for r in results
    ]
    df["Kiruna_Score"] = (
        df["Kiruna_Topic"].map(config.TOPIC_SCORE_MAP).fillna(0).astype(int)
    )

    related_count = (df["Kiruna_Related"] == "Yes").sum()
    print(f"[Semantic] Related: {related_count} | Irrelevant: {len(df) - related_count}")

    return df
