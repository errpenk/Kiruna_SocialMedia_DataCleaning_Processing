# reply_keywords.py
# Keyword and pattern definitions for Kiruna reply classification
# Scores follow the schema in the classification design doc:
#   5 = Relocation (core)
#   4 = Mining / Sami / Aerospace / Northern Sweden life
#   3 = Place name / Climate / Tourism
#   2 = Nordic culture
#   1 = Edge mention
#   0 = Irrelevant / delete

import re

# Score 5: Church or city relocation
RELOCATION_PATTERNS = [
    r"church\s+(move|moving|relocat)",
    r"moving\s+(the\s+)?(city|town|church|building)",
    r"relocat\w*\s+(city|town|church|building)",
    r"torn\s+down",
    r"make\s+way\s+for",
    r"flytt\w*",          # Swedish: move/relocation
    r"samh.lls?flytt",    # Swedish: community relocation
    r"dismantl",
    r"new\s+location",
    r"new\s+site",
]

# Score 4: Aerospace and space industry
AEROSPACE_PATTERNS = [
    r"\besrange\b",
    r"\brexus\b",
    r"\bbexus\b",
    r"rocket\s+launch",
    r"space\s+launch",
    r"\bsatellite\b",
    r"aerospace",
]

# Score 4: Mining and traditional industry
MINING_PATTERNS = [
    r"\bmine\b",
    r"\bmining\b",
    r"\blkab\b",
    r"iron\s+ore",
    r"iron-ore",
    r"mining\s+town",
    r"\bmalm\b",
    r"\bgruva\b",
    r"luossavaara",
    r"open\s+pit",
    r"underground\s+mine",
]

# Score 4: Sami culture and reindeer
SAMI_PATTERNS = [
    r"\bsami\b",
    r"\bs.mi\b",
    r"\bsaami\b",
    r"reindeer",
    r"\bsameby\b",
    r"\bjoik\b",
    r"indigenous\s+swed",
    r"\burfolk\b",
]

# Score 4: Life in northern Sweden (not purely tourism)
NORTHERN_LIFE_PATTERNS = [
    r"life\s+in\s+(kiruna|northern\s+sweden|the\s+arctic)",
    r"living\s+in\s+kiruna",
    r"daily\s+life",
    r"local\s+life",
    r"\bbadhus\b",
    r"\bnybyggt\b",
    r"permafrost",
    r"extreme\s+cold",
    r"polar\s+dark",
]

# Score 3: Place name mentions
PLACE_NAME_PATTERNS = [
    r"\bkiruna\b",
    r"\babisko\b",
    r"\bnorrbotten\b",
    r"\barctic\b",
    r"northern\s+sweden",
    r"north\s+sweden",
    r"swedish\s+lapland",
    r"\bnorrland\b",
    r"arctic\s+circle",
    r"\bgallivare\b",
    r"g.llivare",
    r"\bbjorkliden\b",
    r"bj.rkliden",
    r"riksgr.nsen",
]

# Score 3: Climate and nature
CLIMATE_PATTERNS = [
    r"midnight\s+sun",
    r"polar\s+night",
    r"polar\s+day",
    r"northern\s+lights",
    r"\baurora\b",
    r"\bmosquito",
    r"arctic\s+weather",
    r"arctic\s+climate",
]

# Score 3: Tourism and activities
TOURISM_PATTERNS = [
    r"dog\s+sledding",
    r"dog\s+sled",
    r"ice\s+hotel",
    r"icehotel",
    r"\bskiing\b",
    r"\bhiking\b",
    r"\btourist\b",
    r"\btourism\b",
    r"snowmobile",
    r"husky\s+tour",
    r"aurora\s+tour",
]

# Score 2: General Nordic or Swedish culture
NORDIC_CULTURE_PATTERNS = [
    r"\bswedish\b",
    r"\bnordic\b",
    r"\bscandinavian\b",
    r"\bfika\b",
    r"\blagom\b",
    r"\bviking\b",
    r"sweden\b",
]

# Score 1: Edge mentions (short positive/observational reactions)
EDGE_EMOTION_WORDS = [
    "cool", "nice", "wow", "sad", "interesting",
    "damn", "amazing", "incredible", "impressive",
]

EDGE_CONTEXT_WORDS = ["this", "here", "there", "that"]

EDGE_CONTENT_MAX_LEN = 20
EDGE_CONTENT_MIN_LEN = 5

# Noise filters

# Patterns that mark a reply as an advertisement
AD_PATTERNS = [
    r"http[s]?://",
    r"www\.",
    r"\bdiscount\b",
    r"\bpromo\b",
]

# Patterns that mark a reply as fully meaningless (single tag or symbol run)
MEANINGLESS_PATTERNS = [
    r"^@\w+$",
    r"^#\w+$",
    r"^[#\s\u271d]+$",
]

# Short content that is still worth keeping
SHORT_KEEP_WORDS = ["man", "wow", "thanks", "cool", "nice", "sad", "damn"]
SHORT_KEEP_EMOTIONS = [r":\(", r":\)", r":D", r"xD"]
SHORT_MIN_LEN = 6

# Delete threshold
KEEP_SCORE_THRESHOLD = 3
