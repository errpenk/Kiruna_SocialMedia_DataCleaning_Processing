# All keywords, exclusion patterns, and file path configurations

# Route
INPUT_FILE  = 'post_data.xlsx'
OUTPUT_FILE = 'post_data_cleaned.xlsx'
SHEET_NAME  = 'post data'

# Combine
TITLE_COL   = 'Title'
BODY_COL    = 'selftext'   # optional; None


# Directly related keywords (including Kiruna)
KIRUNA_DIRECT = [
    r'\bkiruna\b',
]
if

# Indirectly related keywords (categorized by topic)
# For each major category, matching just one pattern is considered a match for that category
INDIRECT_KEYWORDS = {
    'northern_sweden': [
        r'\bnorthern\s+sweden\b',
        r'\bnorrbotten\b',          # Modify
        r'\blapland\b',
        r'\bnorrland\b',
        r'\bnordic\s+hinterland\b',
        r'\bswedish\s+arctic\b',
    ],
    'mining': [
        r'\bmining\b',
        r'\bmine\b',
        r'\biron\s+ore\b',
        r'\blkab\b',
        r'\bgruva\b',
        r'\bgruvchocken\b',
        r'\bmalm\b',
        r'\bbergbau\b',
        r'\bminerai\b',
        r'\bopen[\s-]pit\b',
        r'\bunderground\s+mine\b',
    ],
    'relocation': [
        r'\brelocat',               # relocate / relocation / relocating
        r'\bmoving\b',
        r'\bmove\b',
        r'\bmoved\b',
        r'\bdisplac',               # displaced / displacement
        r'\bresettl',               # resettle / resettlement
        r'\bevacuat',               # evacuate / evacuation
        r'\babandoned\s+town\b',
        r'\btown\s+mov',
        r'\bcity\s+mov',
        r'\bflytta\b',
        r'\bflytten\b',
        r'\bomläggning\b',
        r'\bumsiedlung\b',
        r'\bdéplacement\b',
    ],
    'sami_culture': [
        r'\bsami\b',
        r'\bsámi\b',
        r'\blapp\b',
        r'\bindigenous.*sweden\b',
        r'\breindeer\s+herding\b',
    ],
    'rare_earth': [
        r'\brare[\s-]earth\b',
        r'\bcritical\s+mineral',
        r'\bsällsynta\s+jordarter\b',
    ],
    'ice_hotel': [
        r'\bice[\s-]hotel\b',
        r'\bis-hotell\b',
        r'\bicehotel\b',
    ],
    'church': [
        r'\bkiruna\s+church\b',     # Modify
        r'\bkyrka\b',
        r'\bkirche\b',
    ],
}

# Core Topic Combinations (used for confidence weighting)
# Hitting multiple core categories simultaneously, higher confidence
CORE_CATEGORIES = {'relocation', 'mining', 'northern_sweden'}


# Exclusion Mode
# Exclusion checks are executed before direct/indirect operations.
EXCLUSION_PATTERNS = [
    r'\bgame\b.*\bdlc\b',
    r'\bnordic\s+horizons\b',
    r'\bcleaning\s+fee\b',
    r'\bend\s+of\s+tenancy\b',
    r'\bsan\s+francisco\b',
    r'\bstockholm\b(?!.*\bkiruna\b)',   # Stockholm but not Kiruna
    r'\breal\s+estate\b(?!.*\bkiruna\b)',
    r'\bairbnb\b',
]
