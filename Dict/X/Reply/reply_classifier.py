
# Scoring-based classifier for Kiruna reply data
# Each reply receives a Kiruna_Score from 0 to 5
# Only replies with Kiruna_Score >= KEEP_SCORE_THRESHOLD are kept

import re
import pandas as pd
from typing import Tuple, List

from reply_keywords import (
    RELOCATION_KEYWORDS,
    MINING_KEYWORDS,
    SAMI_KEYWORDS,
    NEW_INDUSTRY_KEYWORDS,
    PLACE_NAME_KEYWORDS,
    LOCAL_LIFE_KEYWORDS,
    TOURISM_KEYWORDS,
    NORDIC_CULTURE_KEYWORDS,
    EDGE_KEYWORDS,
    POLITICAL_SENSITIVE_KEYWORDS,
    OFF_TOPIC_LOCATIONS,
    COMPARISON_CONTEXT_KEYWORDS,
    SPAM_SHORT_LINK_PATTERNS,
    SPAM_HASHTAG_THRESHOLD,
    KEEP_SCORE_THRESHOLD,
)

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


# low-level text helpers

def _norm(text) -> str:
    if pd.isna(text):
        return ""
    return str(text).strip().lower()


def _contains_any(text_lower: str, keywords: List[str]) -> bool:
    return any(kw in text_lower for kw in keywords)


# noise / spam checks

def is_empty_or_noise(text) -> bool:
    raw = _norm(text)
    if not raw:
        return True
    if raw.isspace():
        return True
    if re.match(r"^[\W_]+$", raw):
        return True
    if len(EMOJI_PATTERN.sub("", raw).strip()) == 0:
        return True
    return False


def is_spam(text) -> bool:
    raw = "" if pd.isna(text) else str(text)
    hashtag_count = len(re.findall(r"#\w+", raw))
    has_short_link = any(re.search(p, raw) for p in SPAM_SHORT_LINK_PATTERNS)
    return hashtag_count >= SPAM_HASHTAG_THRESHOLD and has_short_link


# delete-flag checks

def is_political_sensitive(text) -> bool:
    t = _norm(text)
    return _contains_any(t, POLITICAL_SENSITIVE_KEYWORDS)


def is_off_topic_location(text) -> bool:
    t = _norm(text)
    for loc in OFF_TOPIC_LOCATIONS:
        if loc in t:
            if not _contains_any(t, COMPARISON_CONTEXT_KEYWORDS + ["sweden", "swedish", "kiruna"]):
                return True
    return False


# scoring engine

def compute_score(text) -> Tuple[int, List[str]]:
    t = _norm(text)
    matched_topics = []
    max_score = 0

    topic_map = [
        (5, "Relocation",      RELOCATION_KEYWORDS),
        (4, "Mining_Industry", MINING_KEYWORDS),
        (4, "Sami_Culture",    SAMI_KEYWORDS),
        (4, "New_Industry",    NEW_INDUSTRY_KEYWORDS),
        (3, "Place_Name",      PLACE_NAME_KEYWORDS),
        (3, "Local_Life",      LOCAL_LIFE_KEYWORDS),
        (3, "Tourism",         TOURISM_KEYWORDS),
        (2, "Nordic_Culture",  NORDIC_CULTURE_KEYWORDS),
        (1, "Edge_Mention",    EDGE_KEYWORDS),
    ]

    for score, label, keywords in topic_map:
        if _contains_any(t, keywords):
            matched_topics.append(label)
            if score > max_score:
                max_score = score

    return max_score, matched_topics


# main entry point

def classify_reply(text) -> Tuple[int, str, List[str], str]:
    """
    Returns
    -------
    (kiruna_score, keep_delete, matched_topics, delete_reason)
        kiruna_score  : 0-5
        keep_delete   : KEEP or DELETE
        matched_topics: list of matched topic labels
        delete_reason : explanation when DELETE, empty string when KEEP
    """
    if is_empty_or_noise(text):
        return (0, "DELETE", [], "empty/noise")

    if is_spam(text):
        return (0, "DELETE", [], "spam")

    if is_political_sensitive(text):
        return (0, "DELETE", [], "political/sensitive content")

    if is_off_topic_location(text):
        return (0, "DELETE", [], "off-topic location")

    score, topics = compute_score(text)

    if score >= KEEP_SCORE_THRESHOLD:
        return (score, "KEEP", topics, "")
    else:
        reason = f"low score ({score})" if score > 0 else "no relevant keywords"
        return (score, "DELETE", topics, reason)
