import pandas as pd
import re
from typing import Tuple


def load_data(file_path: str, sheet_name: str = "post data") -> pd.DataFrame:
    """Load Excel data"""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def is_empty_or_symbols(text: str) -> bool:
    """
    Check whether the content is empty or contains only symbols/emojis
    """
    if pd.isna(text):
        return True
    
    text_str = str(text).strip()
    
    # Empty string
    if not text_str:
        return True
    
    # Emoji URL only
    if re.match(r'^https://abs-0\.twimg\.com/emoji/', text_str):
        return True
    
    # URL only (no other text)
    if re.match(r'^https?://[^\s]+$', text_str):
        return True
    
    # Check whether anything meaningful remains after excluding letters, numbers,
    # Chinese characters, and Swedish special characters
    # Keep a-z, A-Z, å, ä, ö, Å, Ä, Ö, and digits
    meaningful_pattern = r'[a-zA-ZåäöÅÄÖ0-9]'
    if not re.search(meaningful_pattern, text_str):
        return True
    
    return False


def is_advertisement(text: str) -> bool:
    """
    Check whether the content is an advertisement / promotional post
    Rule: 6+ hashtags + short link
    """
    if pd.isna(text):
        return False
    
    text_str = str(text)
    
    # Count hashtags
    hashtags = re.findall(r'#\w+', text_str)
    hashtag_count = len(hashtags)
    
    # Check short links
    short_links = re.findall(r'(bit\.ly|infl\.tv|reut\.rs)/\w+', text_str)
    
    # 6+ hashtags and short link = advertisement
    if hashtag_count >= 6 and len(short_links) > 0:
        return True
    
    return False


def is_kiruna_relocation_related(text: str) -> bool:
    """
    Check whether the post is related to Kiruna relocation
    
    Keyword matching logic:
    - Must contain a location keyword (kiruna/church/mine/city)
    - And must contain an action keyword
      (relocat/move/transfer/transport/shift/flytt/bless/wheel/demolish/rebuild/expand)
    """
    if pd.isna(text):
        return False
    
    text_lower = str(text).lower()
    
    # Location-related keywords
    location_keywords = [
        'kiruna', 'church', 'mine', 'city',
        'kyrka', 'gruva', 'stad'  # Swedish
    ]
    
    # Relocation/action keywords
    action_keywords = [
        'relocat', 'move', 'transfer', 'transport', 'shift',
        'flytt', 'flyttas', 'flyttning',  # Swedish
        'bless', 'wheel', 'demolish', 'rebuild', 'expand',
        'new location', 'new site', 'new home',
        'moved', 'moving', 'transported', 'transporting'
    ]
    
    # Check whether both location and action keywords are present
    has_location = any(kw in text_lower for kw in location_keywords)
    has_action = any(kw in text_lower for kw in action_keywords)
    
    # Special cases: directly contains "Kiruna relocation" or "Kiruna forever" (exhibition title)
    direct_matches = [
        'kiruna relocation',
        'kiruna forever',
        'relocation of kiruna',
        'kiruna church',
        'kiruna city'
    ]
    has_direct_match = any(kw in text_lower for kw in direct_matches)
    
    return (has_location and has_action) or has_direct_match


def classify_post(text: str) -> Tuple[str, str]:
    """
    Classify a post as KEEP or DELETE
    
    Returns: (classification result, deletion reason)
    """
    # Check empty content / symbols
    if is_empty_or_symbols(text):
        return ("DELETE", "empty/symbols only")
    
    # Check advertisement
    if is_advertisement(text):
        return ("DELETE", "advertisement")
    
    # Check whether related to Kiruna relocation
    if not is_kiruna_relocation_related(text):
        return ("DELETE", "unrelated topic")
    
    return ("KEEP", "")


def clean_posts(df: pd.DataFrame, content_column: str = "Title/Description") -> pd.DataFrame:
    """
    Perform data cleaning
    
    Parameters:
        df: original DataFrame
        content_column: column name containing post content
    
    Returns:
        cleaned DataFrame
    """
    # Create classification results
    df['Keep/Delete'] = 'KEEP'
    df['Deletion_Reason'] = ''
    
    for idx in df.index:
        text = df.loc[idx, content_column]
        classification, reason = classify_post(text)
        df.loc[idx, 'Keep/Delete'] = classification
        df.loc[idx, 'Deletion_Reason'] = reason
    
    # Statistics of deletion reasons
    deletion_stats = df[df['Keep/Delete'] == 'DELETE']['Deletion_Reason'].value_counts()
    print("\n=== Deletion Reason Statistics ===")
    print(deletion_stats)
    
    # Filter kept data
    df_cleaned = df[df['Keep/Delete'] == 'KEEP'].copy()
    
    # Remove helper columns
    df_cleaned = df_cleaned.drop(columns=['Keep/Delete', 'Deletion_Reason'])
    
    # Secondary cleaning: remove empty rows and single-character rows
    df_cleaned = df_cleaned[df_cleaned[content_column].apply(
        lambda x: not (pd.isna(x) or len(str(x).strip()) <= 1)
    )]
    
    # Reset index
    df_cleaned = df_cleaned.reset_index(drop=True)
    
    return df_cleaned


def main():
    """Main function"""
    # File paths
    input_file = "kiruna_posts.xlsx"
    output_file = "kiruna_posts_cleaned.xlsx"
    
    print("=" * 60)
    print("Kiruna Relocation Post Data Cleaning")
    print("=" * 60)
    
    # Load data
    print(f"\n[1/4] Loading data: {input_file}")
    df = load_data(input_file)
    print(f"      Original data size: {len(df)} posts")
    
    # Perform cleaning
    print(f"\n[2/4] Performing data cleaning...")
    df_cleaned = clean_posts(df)
    
    # Summary statistics
    print(f"\n[3/4] Cleaning summary:")
    print(f"      Kept posts: {len(df_cleaned)} ({len(df_cleaned)/len(df)*100:.1f}%)")
    print(f"      Deleted posts: {len(df) - len(df_cleaned)} ({(len(df)-len(df_cleaned))/len(df)*100:.1f}%)")
    
    # Save results
    print(f"\n[4/4] Saving cleaned data: {output_file}")
    df_cleaned.to_excel(output_file, index=False)
    
    print("\n" + "=" * 60)
    print("Cleaning completed!")
    print("=" * 60)
    
    # Show sample data
    print("\n=== Sample of Cleaned Data (First 5 Rows) ===")
    print(df_cleaned[['Title/Description']].head())
    
    return df_cleaned


if __name__ == "__main__":
    df_result = main()
