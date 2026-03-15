"""
config.py
---------
Central configuration for the Kiruna classifier pipeline.
Edit this file to switch modes, adjust thresholds, or update file paths.
"""

import os

# ---------------------------------------------------------------------------
# Pipeline mode
# ---------------------------------------------------------------------------
# "semantic" : local sentence-transformers only (no API key required)
# "llm"      : Anthropic Claude API only (most accurate)
# "hybrid"   : semantic pre-filter + LLM for uncertain cases (recommended)
MODE: str = "hybrid"

# ---------------------------------------------------------------------------
# Plan A — semantic similarity
# ---------------------------------------------------------------------------
# Cosine similarity threshold below which a comment is considered irrelevant.
# Range: 0.0 – 1.0. Raise to be stricter; lower to capture more borderline text.
SEMANTIC_THRESHOLD: float = 0.30

# Embedding model from sentence-transformers.
# paraphrase-multilingual-MiniLM-L12-v2 supports 50+ languages including
# English, Swedish, Finnish, and Chinese out of the box.
SEMANTIC_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

# Natural-language anchor phrases that represent each Kiruna topic.
# The model converts these to embeddings and compares them against each comment.
# No keyword lists needed — the model understands semantic meaning.
SEMANTIC_ANCHORS: list[str] = [
    "Kiruna city relocation urban planning Sweden",
    "Kiruna mine LKAB iron ore mining",
    "Kiruna church heritage building move",
    "Sami indigenous people reindeer herding northern Sweden",
    "Swedish Lapland arctic tourism northern lights",
    "Esrange rocket launch aerospace Kiruna",
    "Norrbotten region Sweden",
    "midnight sun polar night Kiruna",
]

# Maps each anchor index to a topic label (must stay aligned with SEMANTIC_ANCHORS).
ANCHOR_TOPIC_MAP: list[str] = [
    "Church/City Relocation",
    "Mining/Industry",
    "Church/City Relocation",
    "Sami Culture",
    "Tourism/Activities",
    "Aerospace",
    "Place Name",
    "Climate/Nature",
]

# ---------------------------------------------------------------------------
# Plan B — LLM (Anthropic Claude)
# ---------------------------------------------------------------------------
# API key is read from the environment variable ANTHROPIC_API_KEY by default.
# You can also paste the key directly here, but avoid committing it to git.
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")

# Claude model to use for classification calls.
LLM_MODEL: str = "claude-sonnet-4-20250514"

# Number of comments sent to the LLM in a single API request.
# Larger batches reduce API call overhead; smaller batches improve JSON reliability.
LLM_BATCH_SIZE: int = 15

# Maximum tokens the LLM is allowed to generate per batch response.
LLM_MAX_TOKENS: int = 1500

# Seconds to sleep between successive API calls (rate-limit safeguard).
LLM_SLEEP_BETWEEN_BATCHES: float = 0.3

# Number of retry attempts if an API call fails.
LLM_MAX_RETRIES: int = 3

# ---------------------------------------------------------------------------
# Hybrid mode thresholds
# ---------------------------------------------------------------------------
# Comments with semantic score >= HYBRID_HIGH_THRESHOLD are accepted as
# relevant immediately (no LLM needed).
# Comments with semantic score < SEMANTIC_THRESHOLD are rejected immediately.
# Comments in between are sent to the LLM for a final judgment.
HYBRID_HIGH_THRESHOLD: float = 0.40

# ---------------------------------------------------------------------------
# Topic scoring
# ---------------------------------------------------------------------------
# Scores assigned to each topic label. Used for High_Value tagging and
# deletion recommendations. Topics not listed here default to 0.
TOPIC_SCORE_MAP: dict[str, int] = {
    "Church/City Relocation": 5,
    "Mining/Industry":        4,
    "Aerospace":              4,
    "Sami Culture":           4,
    "Climate/Nature":         3,
    "Place Name":             3,
    "Tourism/Activities":     3,
    "Nordic Life/Culture":    2,
    "Irrelevant":             0,
}

# A comment is marked High_Value when its Kiruna_Score >= this threshold.
HIGH_VALUE_THRESHOLD: int = 4

# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
INPUT_FILE:  str = "kiruna_raw_data.xlsx"
OUTPUT_FILE: str = "kiruna_reply_data_cleaned_smart.xlsx"
SHEET_NAME:  str = "reply data"
