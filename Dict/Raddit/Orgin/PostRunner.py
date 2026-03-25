import pandas as pd
import re
from typing import Tuple, List
import openpyxl


# 1. Config
INPUT_FILE = 'post_data.xlsx' 
OUTPUT_FILE = 'post_data_cleaned.xlsx' 
SHEET_NAME = 'post data'  


# 2. Keywords

# Directly related: Various variants of Kiruna (case-insensitive)
KIRUNA_DIRECT = [
    r'\bkiruna\b',
]

# Indirect related keyword classification
INDIRECT_KEYWORDS = {
    'northern_sweden': [
        r'\bnorthern\s+sweden\b',
        r'\nnorrbotten\b',
        r'\blapland\b',
        r'\bnorrland\b',
        r'\nordic\s+hinterland\b',
    ],
    'mining': [
        r'\bmining\b',
        r'\bmine\b',
        r'\biron\s+ore\b',
        r'\blkab\b',  # Swedish mining company
        r'\bgruva\b',  # Swedish: mine
        r'\bgruvchocken\b',  # Swedish: mine tremor
        r'\bmalm\b',  # Swedish: ore
        r'\bbergbau\b',  # German: mining
        r'\bminerai\b',  # French: ore
    ],
    'relocation': [
        r'\brelocat',  # relocate, relocation, relocating
        r'\bmoving\b',
        r'\bmove\b',
        r'\bmoved\b',
        r'\bflytta\b',  # Swedish: relocation
        r'\bflytten\b',
        r'\bomläggning\b',
        r'\bumsiedlung\b',  # German: relocation
        r'\bdéplacement\b',  # French: relocation
    ],
    'sami_culture': [
        r'\bsami\b',
        r'\bsámi\b',
        r'\blapp\b',  
    ],
    'rare_earth': [
        r'\brare\s+earth\b',
        r'\bsällsynta\s+jordarter\b',  # Swedish
    ],
    'ice_hotel': [
        r'\bice\s+hotel\b',
        r'\bis-hotell\b',  # Swedish
    ],
    'church': [
        r'\bchurch\b',
        r'\bkyrka\b',  # Swedish
        r'\bkirche\b',  # German
    ],
}

# Exclude keywords (even if a post matches the keywords above, if it also matches these patterns it will be considered irrelevant)
EXCLUSION_PATTERNS = [
    r'\bgame\b.*\bdlc\b',  # game DLC
    r'\bnordic\s+horizons\b',  # game
    r'\bcleaning\s+fee\b',  
    r'\bend\s+of\s+tenancy\b',  
    r'\bsan\s+francisco\b',  
    r'\bstockholm\b(?!.*\bkiruna)',  # Stockholm (unless Kiruna is mentioned at the same time)
]


# 3. Core classification function

def preprocess_text(text: str) -> str:
    """
    Text preprocessing: convert to lowercase and remove extra spaces
    """
    if pd.isna(text):
        return ''
    return str(text).lower().strip()

def check_direct_kiruna(text: str) -> bool:
    """
    Check whether the post is directly related (contains Kiruna)
    """
    text_lower = preprocess_text(text)
    for pattern in KIRUNA_DIRECT:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def check_indirect_keywords(text: str) -> Tuple[bool, List[str]]:
    """
    Check indirectly related keywords and return matched categories
    """
    text_lower = preprocess_text(text)
    matched_categories = []
    
    for category, patterns in INDIRECT_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                matched_categories.append(category)
                break  # Each category recorded only once
    
    # A match must appear in at least one category to be considered indirectly related
    is_indirect = len(matched_categories) >= 1
    return is_indirect, matched_categories

def check_exclusions(text: str) -> bool:
    """
    Check whether the post should be excluded (marked as irrelevant)
    """
    text_lower = preprocess_text(text)
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def classify_post(title: str) -> Tuple[int, str, float]:
    """
    Classify a single post

    Parameters:
        title: Post title

    Returns:
        tuple: (Category code, Classification reason, Confidence score)
        - Category code: 1 = Directly relevant, 2 = Indirectly relevant, 0 = Irrelevant
        - Confidence score: 0.0–1.0
    """
    if pd.isna(title):
        return 0, 'Empty title', 0.95
    
    # Layer 1: Check direct relevance
    if check_direct_kiruna(title):
        return 1, 'Kiruna mentioned directly', 0.95
    
    # Check exclusion patterns
    if check_exclusions(title):
        return 0, 'Exclude pattern matching', 0.90
    
    # Layer 2: Check indirect relevance
    is_indirect, matched_cats = check_indirect_keywords(title)
    if is_indirect:
        confidence = min(0.85 + 0.05 * len(matched_cats), 0.95)
        reason = f"Indirectly related: {', '.join(matched_cats)}"
        return 2, reason, confidence
    
    # Layer 3: Default to irrelevant
    return 0, 'No matching keywords', 0.85


# 4. Main processing workflow

def load_data(file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load Excel data
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    print(f"✓ Loading completed: {len(df)} rows")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform data cleaning and classification
    """
    # Apply classification function
    classification_results = df['Title'].apply(classify_post)
    
    # Parse results
    df['Cleaned_Category'] = [x[0] for x in classification_results]
    df['Classification_Reason'] = [x[1] for x in classification_results]
    df['Confidence'] = [x[2] for x in classification_results]
    
    # Add keep flag
    df['Keep'] = df['Cleaned_Category'].isin([1, 2])
    
    print("✓ Data cleaning completed")
    return df

def generate_report(df: pd.DataFrame) -> dict:
    """
    Generate statistical report
    """
    report = {
        'total_posts': len(df),
        'direct_related': len(df[df['Cleaned_Category'] == 1]),
        'indirect_related': len(df[df['Cleaned_Category'] == 2]),
        'unrelated': len(df[df['Cleaned_Category'] == 0]),
        'to_keep': len(df[df['Keep'] == True]),
        'to_delete': len(df[df['Keep'] == False]),
        'avg_confidence': df['Confidence'].mean(),
    }
    
    report['direct_pct'] = report['direct_related'] / report['total_posts'] * 100
    report['indirect_pct'] = report['indirect_related'] / report['total_posts'] * 100
    report['unrelated_pct'] = report['unrelated'] / report['total_posts'] * 100
    
    return report

def save_results(df: pd.DataFrame, output_path: str, report: dict):
    """
    Save cleaned results and report
    """
    # Save full dataset with classification results
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"✓ Results saved to: {output_path}")
    
    # Print report
    print("\n" + "="*60)
    print("KIRUNA POST DATA CLEANING REPORT")
    print("="*60)
    print(f"Total posts: {report['total_posts']}")
    print(f"\nClassification results:")
    print(f" Directly related (keep): {report['direct_related']} ({report['direct_pct']:.1f}%)")
    print(f" Indirectly related (keep): {report['indirect_related']} ({report['indirect_pct']:.1f}%)")
    print(f" Irrelevant (remove): {report['unrelated']} ({report['unrelated_pct']:.1f}%)")
    print(f"\nSuggested action:")
    print(f" Posts to keep: {report['to_keep']}")
    print(f" Posts to delete: {report['to_delete']}")
    print(f"\nAverage confidence: {report['avg_confidence']:.2f}")
    print("="*60)


# 5. Execution entry

if __name__ == '__main__':
    print("Starting Kiruna post data cleaning...\n")
    
    # Load data
    df = load_data(INPUT_FILE, SHEET_NAME)
    
    # Clean data
    df_cleaned = clean_data(df)
    
    # Generate report
    report = generate_report(df_cleaned)
    
    # Save results
    save_results(df_cleaned, OUTPUT_FILE, report)
    
    print("\n✓ Cleaning process completed!")
