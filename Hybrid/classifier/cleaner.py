"""
cleaner.py
----------
Step 1 of the pipeline: load raw Excel data and apply rule-based filters
to remove noise before any classification work begins.

Filters applied (in order):
  1. Empty content or punctuation-only strings
  2. Advertisement / spam URLs
  3. Structurally meaningless strings (@mention only, hashtag only, etc.)
  4. Strings that are too short to carry any information
"""

import re
import pandas as pd
from typing import Tuple, List, Dict


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_and_clean(file_path: str, sheet_name: str = "reply data") -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Load the Excel file and run the initial noise-removal pass.

    Returns
    -------
    df_clean     : DataFrame with low-quality rows removed and index reset.
    deleted_rows : List of dicts recording every removed row with its reason.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df["CONTENT"] = df["CONTENT"].fillna("").astype(str)

    original_count = len(df)
    df_clean, deleted_rows = _apply_filters(df)

    print(
        f"[Cleaner] Loaded {original_count} rows | "
        f"Removed {len(deleted_rows)} | "
        f"Remaining {len(df_clean)}"
    )
    return df_clean, deleted_rows


# ---------------------------------------------------------------------------
# Internal filter logic
# ---------------------------------------------------------------------------

def _apply_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    """Iterate over every row and apply all noise filters sequentially."""
    deleted_rows: List[Dict] = []
    indices_to_drop: List[int] = []

    for idx, row in df.iterrows():
        content = row["CONTENT"].strip()
        # Row number as it would appear in Excel (header = row 1, data starts at row 2)
        excel_row = idx + 2

        if _is_empty_or_punctuation_only(content):
            _record(deleted_rows, excel_row, "Empty content or punctuation only", content)
            indices_to_drop.append(idx)

        elif _is_advertisement(content):
            _record(deleted_rows, excel_row, "Advertisement / spam link", content)
            indices_to_drop.append(idx)

        elif _is_structurally_meaningless(content):
            _record(deleted_rows, excel_row, "Structurally meaningless (mention/hashtag only)", content)
            indices_to_drop.append(idx)

        elif _is_too_short_to_be_useful(content):
            _record(deleted_rows, excel_row, "Too short to carry meaning", content)
            indices_to_drop.append(idx)

    df_clean = df.drop(indices_to_drop).reset_index(drop=True)
    return df_clean, deleted_rows


def _record(deleted_rows: List[Dict], row_num: int, reason: str, content: str) -> None:
    """Append a deletion record to the log list."""
    deleted_rows.append({
        "row":     row_num,
        "reason":  reason,
        "content": content[:80],  # truncate for readability
    })


# ---------------------------------------------------------------------------
# Individual filter predicates
# ---------------------------------------------------------------------------

def _is_empty_or_punctuation_only(content: str) -> bool:
    """Return True if the string is blank or contains only punctuation/whitespace."""
    if not content or content.strip() == "":
        return True
    # Strip all non-word characters; if nothing remains, it was punctuation only
    return len(re.sub(r"[^\w\s]", "", content).strip()) == 0


def _is_advertisement(content: str) -> bool:
    """Return True if the content looks like a promotional message or spam link."""
    ad_patterns = [
        r"http[s]?://",   # any URL
        r"www\.",         # bare domain reference
        r"\bdiscount\b",  # promo vocabulary
        r"\bpromo\b",
    ]
    return any(re.search(p, content.lower()) for p in ad_patterns)


def _is_structurally_meaningless(content: str) -> bool:
    """
    Return True if the content is structurally useless:
      - A lone @mention  (e.g. "@username")
      - A lone #hashtag  (e.g. "#topic")
      - Only crosses, spaces, or other decoration symbols
    """
    if re.match(r"^@\w+$", content) or re.match(r"^#\w+$", content):
        return True
    if re.match(r"^[#\s✝]+$", content):
        return True
    return False


def _is_too_short_to_be_useful(content: str) -> bool:
    """
    Return True for very short strings that add no analytical value.
    Exceptions are kept:
      - Common short meaningful words (wow, nice, sad, …)
      - Emoticons that convey sentiment
    """
    if len(content) >= 6:
        return False  # long enough to be worth keeping

    # Short words that still convey a clear reaction
    keep_words = ["man", "wow", "thanks", "cool", "nice", "sad", "damn"]
    if any(w in content.lower() for w in keep_words):
        return False

    # ASCII emoticons that express sentiment
    emoticon_patterns = [r":\(", r":\)", r":D", r"xD"]
    if any(re.search(p, content) for p in emoticon_patterns):
        return False

    return True


# Re-export predicate so other modules can reuse it (e.g. deletion recommender)
is_advertisement = _is_advertisement
