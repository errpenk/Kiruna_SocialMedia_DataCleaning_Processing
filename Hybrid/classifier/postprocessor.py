"""
postprocessor.py
----------------
Post-classification enrichment steps applied after topic labelling:

  1. Language detection   — adds a Lang_Detected column (ISO 639-1 code)
  2. High-value tagging   — adds High_Value = "Yes" / "No"
  3. Deletion recommender — adds Delete_Recommend and Delete_Reason columns

These steps are intentionally separated from classification so they can be
reused or replaced independently without touching the classifier logic.

Dependencies
------------
    pip install langdetect   (optional, only needed for language detection)
"""

import pandas as pd

from kiruna_classifier import config
from kiruna_classifier.cleaner import is_advertisement


# ---------------------------------------------------------------------------
# 1. Language detection
# ---------------------------------------------------------------------------

def detect_languages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attempt to detect the language of each comment using langdetect.

    Adds a Lang_Detected column with ISO 639-1 codes (e.g. "en", "sv", "fi").
    Returns "unknown" for very short strings that cannot be reliably detected.

    If the langdetect package is not installed, a warning is printed and the
    column is not added, so the pipeline continues unaffected.
    """
    try:
        from langdetect import detect, LangDetectException
    except ImportError:
        print(
            "[PostProcessor] langdetect not installed — skipping language detection.\n"
            "  Install with:  pip install langdetect"
        )
        return df

    langs = []
    for text in df["CONTENT"]:
        try:
            langs.append(detect(text))
        except LangDetectException:
            langs.append("unknown")

    df = df.copy()
    df["Lang_Detected"] = langs
    return df


# ---------------------------------------------------------------------------
# 2. High-value tagging
# ---------------------------------------------------------------------------

def tag_high_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mark each comment as High_Value = "Yes" if its Kiruna_Score meets or
    exceeds the configured threshold (config.HIGH_VALUE_THRESHOLD).
    """
    df = df.copy()
    df["High_Value"] = df["Kiruna_Score"].apply(
        lambda score: "Yes" if score >= config.HIGH_VALUE_THRESHOLD else "No"
    )
    return df


# ---------------------------------------------------------------------------
# 3. Deletion recommendations
# ---------------------------------------------------------------------------

def add_deletion_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recommend deletion for comments that offer no analytical value.

    A comment is flagged for deletion when:
      - It is an advertisement or spam link, OR
      - Its Kiruna_Score is 0 AND the content is very short (< 8 characters)

    Adds Delete_Recommend ("Yes" / "No") and Delete_Reason columns.
    """
    df = df.copy()
    df["Delete_Recommend"] = ""
    df["Delete_Reason"]    = ""

    for idx, row in df.iterrows():
        recommend, reason = _evaluate_row(row["Kiruna_Score"], row["CONTENT"])
        df.at[idx, "Delete_Recommend"] = recommend
        df.at[idx, "Delete_Reason"]    = reason

    flagged = (df["Delete_Recommend"] == "Yes").sum()
    print(f"[PostProcessor] Deletion recommended for {flagged} rows.")

    return df


def _evaluate_row(score: int, content: str) -> tuple[str, str]:
    """Return (recommend, reason) for a single row."""
    if is_advertisement(content):
        return "Yes", "Advertisement / spam link"

    if score == 0 and len(content) < 8:
        return "Yes", "Zero score and content too short"

    return "No", ""
