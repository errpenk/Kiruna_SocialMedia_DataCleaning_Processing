# Keyword lists and score definitions for Kiruna reply classification
# Each topic group has an associated relevance score (0-5)

# Score 5: Core topics - direct discussion of Kiruna relocation or the relocation event itself


RELOCATION_KEYWORDS = [
    "relocation", "relocating", "relocate", "relocated",
    "moving the city", "move the city", "moved the city",
    "moving the town", "move the town",
    "moving the church", "move the church", "moved the church",
    "church move", "building move", "moving building",
    "dismantl", "new location", "new site",
    "flytt", "flytta", "flyttar", "flyttning",
    "samhallsflytt", "samhällsflytt",
]

# Score 4: Traditional industry - mining, iron ore, LKAB, Luossavaara
MINING_KEYWORDS = [
    "mining", "mine", "miner", "miners",
    "iron ore", "iron-ore",
    "lkab",
    "luossavaara",
    "open pit", "underground mine",
    "ore", "malm", "gruva", "gruvor",
    "jarnomalm", "järnmalm",
    "steel production", "smelting",
]

# Score 4: Sami and indigenous culture
SAMI_KEYWORDS = [
    "sami", "sámi", "saami",
    "reindeer", "reindeer herding", "reindeer herder",
    "sameby",
    "indigenous", "urfolk",
    "lappland", "lapland",
    "norrland",
]

# Score 4: New industry and technology development
NEW_INDUSTRY_KEYWORDS = [
    "engineer", "engineering",
    "aerospace", "space industry",
    "satellite", "esrange",
    "green steel", "fossil-free steel", "hydrogen steel",
    "ssab",
    "tech hub", "innovation",
    "renewable energy", "wind power", "solar",
]

# Score 3: Place names related to Kiruna region
PLACE_NAME_KEYWORDS = [
    "kiruna",
    "abisko",
    "norrbotten",
    "arctic",
    "arctic circle",
    "swedish lapland",
    "northern sweden", "north sweden",
    "sweden's north",
    "gallivare", "gallivaare", "gällivare",
    "bjorkliden", "björkliden",
    "riksgransen", "riksgränsen",
]

# Score 3: Local daily life in Kiruna or Arctic region
LOCAL_LIFE_KEYWORDS = [
    "midnight sun",
    "polar night", "polar day",
    "northern lights", "aurora borealis", "aurora",
    "mosquito", "mosquitoes",
    "darkness", "dark months",
    "cold weather", "extreme cold",
    "permafrost",
    "badhus",
    "nybyggt",
    "daily life", "local life",
    "living in kiruna", "life in kiruna",
]

# Score 3: Tourism activities
TOURISM_KEYWORDS = [
    "ice hotel", "icehotel",
    "dog sledding", "dog sled", "dogsledding",
    "skiing", "ski resort",
    "snowmobile", "snowmobiling",
    "husky", "husky tour",
    "northern lights tour",
    "aurora tour",
    "visit kiruna", "travel to kiruna",
    "tourist", "tourism",
]

# Score 2: General Nordic or Swedish culture
NORDIC_CULTURE_KEYWORDS = [
    "sweden", "swedish",
    "nordic", "nordic culture",
    "scandinavia", "scandinavian",
    "fika",
    "lagom",
    "swedish design",
    "viking", "vikings",
    "nordic welfare",
]

# Score 1: Edge cases - brief contextual mentions
EDGE_KEYWORDS = [
    "interesting", "fascinating",
    "never knew", "did not know", "didn't know",
    "heard about", "read about",
    "i see", "i noticed",
]

# Content to delete: noise and off-topic categories

# Political or religiously sensitive content
POLITICAL_SENSITIVE_KEYWORDS = [
    "trump",
    "muslim", "muslims",
    "mosque",
    "burn",
    "asylum seeker", "asylum seekers",
    "mohammed",
    "3rd world",
    "immigrants",
    "brann alla kyrkor", "bränn alla kyrkor",
    "ukraine", "ukraina",
    "palestine", "gaza",
]

# Completely off-topic geographic references (only if no comparison context)
OFF_TOPIC_LOCATIONS = [
    "kenya", "kisumu", "nairobi",
    "turkey",
    "tel aviv",
    "hasankeyf",
]

# Words that signal a comparison or analogy context (exempt from off-topic deletion)
COMPARISON_CONTEXT_KEYWORDS = [
    "like", "similar", "compared", "just as", "same as",
    "reminds", "unlike", "analogy",
]

# Spam detection
SPAM_SHORT_LINK_PATTERNS = [
    r"bit\.ly/\w+",
    r"infl\.tv/\w+",
    r"reut\.rs/\w+",
    r"t\.co/\w+",
    r"ow\.ly/\w+",
    r"tinyurl\.com/\w+",
]
SPAM_HASHTAG_THRESHOLD = 6

# Score thresholds
KEEP_SCORE_THRESHOLD = 3
