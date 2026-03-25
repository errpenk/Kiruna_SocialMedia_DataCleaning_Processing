
# Scoring-based classifier for Kiruna reply data
# Returns a Kiruna_Score (0-5), matched topic, and delete recommendation

import re
from typing import Tuple

from reply_keywords import (
    RELOCATION_PATTERNS,
    AEROSPACE_PATTERNS,
    MINING_PATTERNS,
    SAMI_PATTERNS,
    NORTHERN_LIFE_PATTERNS,
    PLACE_NAME_PATTERNS,
    CLIMATE_PATTERNS,
    TOURISM_PATTERNS,
    NORDIC_CULTURE_PATTERNS,
    EDGE_EMOTION_WORDS,
    EDGE_CONTEXT_WORDS,
    EDGE_CONTENT_MIN_LEN,
    EDGE_CONTENT_MAX_LEN,
    AD_PATTERNS,
    MEANINGLESS_PATTERNS,
    SHORT_KEEP_WORDS,
    SHORT_KEEP_EMOTIONS,
    SHORT_MIN_LEN,
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


# noise checks

def is_empty_or_punctuation_only(content: str) -> bool:
    if not content or content.strip() == "":
        return True
    cleaned = re.sub(r"[^\w\s]", "", content).strip()
    no_emoji = EMOJI_PATTERN.sub("", cleaned).strip()
    return len(no_emoji) == 0


def is_advertisement(content: str) -> bool:
    return any(re.search(p, content.lower()) for p in AD_PATTERNS)


def is_meaningless(content: str) -> bool:
    return any(re.match(p, content.strip()) for p in MEANINGLESS_PATTERNS)


def is_too_short_meaningless(content: str) -> bool:
    if len(content) >= SHORT_MIN_LEN:
        return False
    if any(w in content.lower() for w in SHORT_KEEP_WORDS):
        return False
    if any(re.search(p, content) for p in SHORT_KEEP_EMOTIONS):
        return False
    return True


def should_delete_noise(content: str) -> Tuple[bool, str]:
    if is_empty_or_punctuation_only(content):
        return True, "empty content or only punctuation"
    if is_advertisement(content):
        return True, "advertising and promotion"
    if is_meaningless(content):
        return True, "no practical significance"
    if is_too_short_meaningless(content):
        return True, "too short and meaningless"
    return False, ""


# topic detection

def _match_any(text_lower: str, patterns: list) -> bool:
    return any(re.search(p, text_lower) for p in patterns)


def detect_topic(content: str) -> Tuple[str, int]:
    t = content.lower()

    if _match_any(t, RELOCATION_PATTERNS):
        return "Church/City Relocation", 5

    if _match_any(t, AEROSPACE_PATTERNS):
        return "Aerospace Related", 4

    if _match_any(t, MINING_PATTERNS):
        return "Mining/Industry", 4

    if _match_any(t, SAMI_PATTERNS):
        return "Sami Culture/Reindeer", 4

    if _match_any(t, NORTHERN_LIFE_PATTERNS):
        return "Life in Northern Sweden", 4

    if _match_any(t, PLACE_NAME_PATTERNS):
        return "Place Name Related", 3

    if _match_any(t, CLIMATE_PATTERNS):
        return "Climate/Nature", 3

    if _match_any(t, TOURISM_PATTERNS):
        return "Tourism/Activities", 3

    if _match_any(t, NORDIC_CULTURE_PATTERNS):
        return "Nordic Life/Culture", 2

    if _is_edge_case(content):
        return "Edge Mention", 1

    return "Irrelevant", 0


def _is_edge_case(content: str) -> bool:
    if not (EDGE_CONTENT_MIN_LEN <= len(content) <= EDGE_CONTENT_MAX_LEN):
        return False
    t = content.lower()
    if any(w in t for w in EDGE_EMOTION_WORDS):
        return True
    if any(w in t for w in EDGE_CONTEXT_WORDS):
        return True
    return False


# delete recommendation (applied after scoring)

def _has_emotion(content: str) -> bool:
    symbols = [":(", ":)", ":D", "xD"]
    if any(s in content for s in symbols):
        return True
    words = ["sad", "happy", "cool", "nice", "wow", "damn", "interesting", "beautiful"]
    return any(w in content.lower() for w in words)


def _is_question(content: str) -> bool:
    if content.strip().endswith("?"):
        return True
    return any(w in content.lower() for w in ["what", "why", "how", "when", "where"])


def recommend_deletion(score: int, content: str) -> Tuple[str, str]:
    if is_advertisement(content):
        return "Yes", "advertising and promotion"
    if score == 0 and len(content) < 8 and not _has_emotion(content) and not _is_question(content):
        return "Yes", "purely meaningless"
    return "No", ""


# main classification entry point

def classify_reply(content: str) -> Tuple[bool, str, str, int, str, str]:
    """
    Returns
    -------
    (keep, delete_reason_initial, topic, kiruna_score, high_value, delete_recommend, delete_reason_final)

    Returned as a flat tuple in this order:
        keep              : bool  - False means removed in initial cleaning
        initial_reason    : str   - reason for initial deletion (empty if kept)
        topic             : str
        kiruna_score      : int   0-5
        high_value        : str   Yes / No
        delete_recommend  : str   Yes / No
        final_reason      : str   reason for delete recommendation
    """
    # initial noise filter
    noisy, initial_reason = should_delete_noise(content)
    if noisy:
        return False, initial_reason, "Irrelevant", 0, "No", "Yes", initial_reason

    topic, score = detect_topic(content)
    high_value = "Yes" if score >= 4 else "No"
    rec, final_reason = recommend_deletion(score, content)

    return True, "", topic, score, high_value, rec, final_reason
