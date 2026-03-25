import pandas as pd
import numpy as np
import re
from typing import Tuple, List, Dict



# 1. Data loading and preliminary cleaning
def load_and_clean_data(file_path: str, sheet_name: str = 'reply data') -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['CONTENT'] = df['CONTENT'].fillna('').astype(str)
    
    original_count = len(df)
    df_clean, deleted_rows = initial_cleaning(df)
    
    print(f"orginal：{original_count} | delete：{len(deleted_rows)} | after cleaning：{len(df_clean)}")
    return df_clean, deleted_rows

def initial_cleaning(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
    deleted_rows = []
    indices_to_drop = []
    
    for idx, row in df.iterrows():
        content = row['CONTENT'].strip()
        row_num = idx + 2
        
        if is_empty_or_punctuation_only(content):
            deleted_rows.append({'row': row_num, 'reason': 'Empty content or only punctuation', 'content': content[:50]})
            indices_to_drop.append(idx)
        elif is_advertisement(content):
            deleted_rows.append({'row': row_num, 'reason': 'Advertising and promotion', 'content': content[:50]})
            indices_to_drop.append(idx)
        elif is_meaningless(content):
            deleted_rows.append({'row': row_num, 'reason': 'No practical significance', 'content': content[:50]})
            indices_to_drop.append(idx)
        elif is_too_short_meaningless(content):
            deleted_rows.append({'row': row_num, 'reason': 'Too short is meaningless', 'content': content[:50]})
            indices_to_drop.append(idx)
    
    df_clean = df.drop(indices_to_drop).reset_index(drop=True)
    return df_clean, deleted_rows

def is_empty_or_punctuation_only(content: str) -> bool:
    if not content or content.strip() == '':
        return True
    cleaned = re.sub(r'[^\w\s]', '', content).strip()
    return len(cleaned) == 0

def is_advertisement(content: str) -> bool:
    ad_patterns = [r'http[s]?://', r'www\.', r'discount', r'promo']
    return any(re.search(pattern, content.lower()) for pattern in ad_patterns)

def is_meaningless(content: str) -> bool:
    if re.match(r'^@\w+$', content) or re.match(r'^#\w+$', content):
        return True
    if re.match(r'^[#\s✝]+$', content):
        return True
    return False

def is_too_short_meaningless(content: str) -> bool:
    if len(content) >= 6:
        return False
    keep_words = ['man', 'wow', 'thanks', 'cool', 'nice', 'sad', 'damn']
    if any(word in content.lower() for word in keep_words):
        return False
    emotion_patterns = [r':\(', r':\)', r':D', r'xD']
    if any(re.search(pattern, content) for pattern in emotion_patterns):
        return False
    return True


# 2. Kiruna Relevance Classification
def classify_kiruna_relevance(df: pd.DataFrame) -> pd.DataFrame:
    df['Kiruna_Related'] = ''
    df['Kiruna_Topic'] = ''
    
    for idx, row in df.iterrows():
        topic, is_related = determine_topic(row['CONTENT'])
        df.at[idx, 'Kiruna_Related'] = 'Yes' if is_related else 'No'
        df.at[idx, 'Kiruna_Topic'] = topic
    
    return df

def determine_topic(content: str) -> Tuple[str, bool]:
    content_lower = content.lower()
    
    # 5 Class: Church/City Relocation
    if any(re.search(p, content_lower) for p in [
        r'church\s+(move|moving|relocate)', r'moving\s+(the\s+)?(city|town)',
        r'torn\s+down', r'make\s+way\s+for'
    ]):
        return 'Church/City Relocation', True
    
    # 4 Class：Aerospace related
    if any(re.search(p, content_lower) for p in [r'esrange', r'rexus', r'bexus', r'rocket\s+launch']):
        return 'Aerospace related', True
    
    # 4 Class: Mining/Industry
    if any(re.search(p, content_lower) for p in [
        r'\bmine\b', r'\bmining\b', r'\blkab\b', r'iron\s+ore', r'mining\s+town'
    ]):
        return 'Mining/Industry', True
    
    # 4 Class: Sami culture/reindeer
    if any(re.search(p, content_lower) for p in [
        r'\bsami\b', r'\bsámi\b', r'reindeer', r'sameby', r'joik'
    ]):
        return 'Sami culture/reindeer', True
    
    # 3 Class: Place name related
    if any(re.search(p, content_lower) for p in [
        r'\bkiruna\b', r'Kiruna', r'\babisko\b', r'\bnorrbotten\b',
        r'arctic', r'northern\s+sweden'
    ]):
        return 'Place name related', True
    
    # 3 Class: Climate/Nature
    if any(re.search(p, content_lower) for p in [
        r'midnight\s+sun', r'polar\s+night', r'northern\s+lights', r'aurora', r'mosquito'
    ]):
        return 'Climate/Nature', True
    
    # 3 Class: Tourism/Activities
    if any(re.search(p, content_lower) for p in [
        r'dog\s+sledding', r'ice\s+hotel', r'skiing', r'hiking', r'tourist'
    ]):
        return 'Tourism/Activities', True
    
    # 2 Class：Nordic Life/Culture
    if any(re.search(p, content_lower) for p in [
        r'\bswedish\b', r'\bnordic\b', r'\bscandinavian\b', r'fika', r'lagom'
    ]):
        return 'Nordic Life/Culture', True
    
    return 'irrelevant', False


# 3. Kiruna_Score 
def calculate_kiruna_scores(df: pd.DataFrame) -> pd.DataFrame:
    topic_to_score = {
        'Church/City Relocation': 5,
        'Aerospace Related': 4, 
        'Mining/Industry': 4, 
        'Sami Culture/Reindeer': 4, 
        'Life in Northern Sweden': 4,
        'Place Name Related': 3, 
        'Climate/Nature': 3, 
        'Tourism/Activities': 3,
        'Nordic Life/Culture': 2,
        'Irrelevant': 0
    }

    
    df['Kiruna_Score'] = df.apply(
        lambda row: topic_to_score.get(row['Kiruna_Topic'], 0) if row['Kiruna_Topic'] != 'irrelevant' or is_edge_case(row['CONTENT']) else 0,
        axis=1
    )
    return df

def is_edge_case(content: str) -> bool:
    if not (5 <= len(content) <= 20):
        return False
    emotion_words = ['cool', 'nice', 'wow', 'sad', 'interesting', 'damn']
    if any(word in content.lower() for word in emotion_words):
        return True
    if any(word in content.lower() for word in ['this', 'here', 'there', 'that']):
        return True
    return False


# 4. High_Value Mark
def mark_high_value(df: pd.DataFrame) -> pd.DataFrame:
    df['High_Value'] = df['Kiruna_Score'].apply(lambda score: 'Yes' if score >= 4 else 'No')
    return df


# Delete Suggestion
def generate_deletion_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    df['Delete_Recommend'] = ''
    df['Delete_Reason'] = ''
    
    for idx, row in df.iterrows():
        recommend, reason = recommend_deletion(row['Kiruna_Score'], row['CONTENT'])
        df.at[idx, 'Delete_Recommend'] = recommend
        df.at[idx, 'Delete_Reason'] = reason
    
    return df

def recommend_deletion(score: int, content: str) -> Tuple[str, str]:
    if is_advertisement(content):
        return 'Yes', 'advertising and promotion'
    if score == 0 and len(content) < 8 and not has_emotion(content) and not is_question(content):
        return 'Yes', 'purely meaningless'
    return 'No', ''

def has_emotion(content: str) -> bool:
    emotion_symbols = [':(', ':)', ':D', 'xD', '😂']
    if any(symbol in content for symbol in emotion_symbols):
        return True
    emotion_words = ['sad', 'happy', 'cool', 'nice', 'wow', 'damn', 'interesting', 'beautiful']
    return any(word in content.lower() for word in emotion_words)

def is_question(content: str) -> bool:
    return content.strip().endswith('?') or any(word in content.lower() for word in ['what', 'why', 'how', 'when', 'where'])


# Main Processing
def main_workflow(input_file: str, output_file: str):
    print("="*60)
    print("Kiruna data REPLY cleaning Workflow")
    print("="*60)
    
    # Step 1: loading and cleaning
    df, deleted_rows = load_and_clean_data(input_file)
    
    # Step 2: correlation classification
    df = classify_kiruna_relevance(df)
    
    # Step 3: score
    df = calculate_kiruna_scores(df)
    
    # Step 4: High_Value mark
    df = mark_high_value(df)
    
    # Step 5: delete suggestion
    df = generate_deletion_recommendations(df)
    
    # Step 6: export
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='reply data', index=False)
    
    print(f"\nOutput File：{output_file}")
    print(f"列：{list(df.columns)}")
    return df

# Execution
if __name__ == "__main__":
    df = main_workflow('kiruna_raw_data.xlsx', 'kiruna_reply_data_cleaned.xlsx')
