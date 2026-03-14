import pandas as pd
import re
from langdetect import detect, DetectorFactory
from typing import List, Tuple, Dict

# Set langdetect random seed to ensure consistent results
DetectorFactory.seed = 0


# Configuration Section 

class Config:
    """Configuration class - all keywords and rules defined here"""
    
    # Core Kiruna topic keywords
    KIRUNA_RELOCATION_KEYWORDS = [
        'kiruna', 'relocation', 'moving', 'town', 'flytt', 'flytta', 'flyttar'
    ]
    
    KIRUNA_MINING_KEYWORDS = [
        'mining', 'mine', 'lkab', 'iron ore', 'malm', 'gruva', 'gruvbolaget'
    ]
    
    KIRUNA_LOCALLIFE_KEYWORDS = [
        'badhus', 'pool', 'daily', 'life', 'nybyggt'
    ]
    
    SAMI_INDIGENOUS_KEYWORDS = [
        'sámi', 'sami', 'lappland', 'norrland', 'indigenous', 'same'
    ]
    
    KIRUNA_TOURISM_KEYWORDS = [
        'visited', 'been to', 'tourism', 'tourist'
    ]
    
    # Secondary related topic keywords
    ENGINEERING_MOVE_KEYWORDS = [
        'mammoet', '1250 tonnes', '600-ton', '672-ton', 'engineering', 
        'moved it', 'moving it', 'lift'
    ]
    
    CULTURAL_HERITAGE_KEYWORDS = [
        'heritage', 'cultural', 'preserve', 'history', 'historical'
    ]
    
    RELIGIOUS_DISCUSSION_KEYWORDS = [
        'church', 'religion', 'faith', 'god', 'jesus', 'kyrkan', 'kyrka'
    ]
    
    SWEDEN_GENERAL_KEYWORDS = [
        'sweden', 'swedish', "sweden's"
    ]
    
    # Sensitive content keywords
    POLITICAL_SENSITIVE_KEYWORDS = [
        'trump', 'muslims', 'muslim', 'burn', 'mosque', 'asylum seekers',
        'mohammed', '3rd world', 'immigrants'
    ]
    
    # Off-topic location keywords
    OFF_TOPIC_LOCATIONS = [
        'kenya', 'kisumu', 'nairobi', 'turkey', 'tel aviv', 'palestine',
        'gaza', 'ukraine'
    ]
    
    # Emoji regex
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )


# Core Functional Class

class KirunaCommentAnalyzer:
    """Kiruna Comment Analyzer"""
    
    def __init__(self):
        self.config = Config()
        
    def is_empty_or_meaningless(self, text: str) -> bool:
        """Check whether content is empty or meaningless"""
        if pd.isna(text) or text is None:
            return True
        
        text = str(text).strip()
        
        # Empty string
        if len(text) == 0:
            return True
        
        # Only whitespace
        if text.isspace():
            return True
        
        # Only punctuation
        if re.match(r'^[\W_]+$', text):
            return True
        
        # Only emojis
        text_no_emoji = self.config.EMOJI_PATTERN.sub('', text)
        if len(text_no_emoji.strip()) == 0:
            return True
        
        return False
    
    def is_political_sensitive(self, text: str) -> bool:
        """Check whether content contains political/religious sensitive topics"""
        if pd.isna(text):
            return False
        
        text_lower = str(text).lower()
        
        for keyword in self.config.POLITICAL_SENSITIVE_KEYWORDS:
            if keyword.lower() in text_lower:
                if keyword.lower() in ['burn', 'muslim', 'muslims', 'mosque']:
                    negative_contexts = ['burn', 'before', 'hope', 'not', 'won\'t', 'will']
                    if any(ctx in text_lower for ctx in negative_contexts):
                        return True
                else:
                    return True
        
        return False
    
    def is_off_topic_location(self, text: str) -> bool:
        """Check whether the comment refers to completely unrelated locations"""
        if pd.isna(text):
            return False
        
        text_lower = str(text).lower()
        
        for location in self.config.OFF_TOPIC_LOCATIONS:
            if location.lower() in text_lower:
                has_sweden_context = any(
                    kw in text_lower for kw in ['sweden', 'swedish', 'kiruna']
                )
                if not has_sweden_context:
                    return True
        
        return False
    
    def detect_topics(self, text: str) -> List[str]:
        """Detect topic tags in a comment (multi-label supported)"""
        if pd.isna(text):
            return ['Empty_Meaningless']
        
        text_lower = str(text).lower()
        topics = []
        
        # Priority 1: Empty or meaningless
        if self.is_empty_or_meaningless(text):
            return ['Empty_Meaningless']
        
        # Priority 2: Sensitive content
        if self.is_political_sensitive(text):
            topics.append('Political_Sensitive')
        
        # Priority 3: Completely off-topic location
        if self.is_off_topic_location(text):
            topics.append('Off_Topic_Complete')
        
        # Priority 4-8: Core Kiruna topics
        has_kiruna = 'kiruna' in text_lower
        
        if has_kiruna and any(kw in text_lower for kw in self.config.KIRUNA_RELOCATION_KEYWORDS[1:]):
            topics.append('Kiruna_Relocation')
        
        if has_kiruna and any(kw in text_lower for kw in self.config.KIRUNA_MINING_KEYWORDS):
            topics.append('Kiruna_Mining')
        
        if has_kiruna and any(kw in text_lower for kw in self.config.KIRUNA_LOCALLIFE_KEYWORDS):
            topics.append('Kiruna_LocalLife')
        
        if any(kw in text_lower for kw in self.config.SAMI_INDIGENOUS_KEYWORDS):
            topics.append('Sami_Indigenous')
        
        if any(kw in text_lower for kw in self.config.KIRUNA_TOURISM_KEYWORDS):
            if has_kiruna or 'church' in text_lower:
                topics.append('Kiruna_Tourism')
        
        # Secondary topics
        if any(kw in text_lower for kw in self.config.ENGINEERING_MOVE_KEYWORDS):
            topics.append('Engineering_Move')
        
        if any(kw in text_lower for kw in self.config.CULTURAL_HERITAGE_KEYWORDS):
            topics.append('Cultural_Heritage')
        
        if any(kw in text_lower for kw in self.config.RELIGIOUS_DISCUSSION_KEYWORDS):
            if 'Political_Sensitive' not in topics:
                topics.append('Religious_Discussion')
        
        if any(kw in text_lower for kw in self.config.SWEDEN_GENERAL_KEYWORDS):
            if not has_kiruna:
                topics.append('Sweden_General')
        
        if len(topics) == 0:
            topics.append('General')
        
        return topics
    
    def calculate_kiruna_score(self, text: str, topics: List[str]) -> int:
        """Calculate Kiruna relevance score (0–5)"""
        if pd.isna(text):
            return 0
        
        text_lower = str(text).lower()
        has_kiruna = 'kiruna' in text_lower
        
        if self.is_empty_or_meaningless(text):
            return 0
        if 'Political_Sensitive' in topics or 'Off_Topic_Complete' in topics:
            return 0
        
        if has_kiruna:
            if ('Kiruna_Relocation' in topics or 
                'Kiruna_Mining' in topics or 
                'Kiruna_LocalLife' in topics):
                return 5
            return 4
        
        if 'Sami_Indigenous' in topics:
            return 4
        if any(kw in text_lower for kw in ['arctic', 'northern sweden', 'lappland']):
            return 4
        
        if ('Engineering_Move' in topics or 
            'Cultural_Heritage' in topics):
            return 3
        if 'Religious_Discussion' in topics:
            if any(kw in text_lower for kw in self.config.ENGINEERING_MOVE_KEYWORDS):
                return 3
            return 3
        
        if 'Sweden_General' in topics:
            return 2
        
        return 1
    
    def is_high_value(self, score: int, topics: List[str]) -> int:
        """Determine whether a comment is high-value"""
        if score >= 4:
            return 1
        
        core_topics = [
            'Kiruna_Relocation', 'Kiruna_Mining', 'Kiruna_LocalLife',
            'Sami_Indigenous', 'Kiruna_Tourism'
        ]
        if any(topic in topics for topic in core_topics):
            return 1
        
        return 0
    
    def get_delete_recommend(self, topics: List[str]) -> int:
        """Determine whether deletion is recommended"""
        if 'Empty_Meaningless' in topics:
            return 1
        if 'Political_Sensitive' in topics:
            return 1
        if 'Off_Topic_Complete' in topics:
            return 1
        return 0
    
    def get_delete_reason(self, topics: List[str]) -> str:
        """Get deletion reason"""
        if 'Empty_Meaningless' in topics:
            return 'Empty content or punctuation only'
        if 'Political_Sensitive' in topics:
            return 'Political or religious sensitive content'
        if 'Off_Topic_Complete' in topics:
            return 'Completely unrelated topic'
        return ''
    
    def detect_language(self, text: str) -> str:
        """Detect language of the comment"""
        if pd.isna(text) or len(str(text).strip()) < 10:
            return 'unknown'
        
        try:
            lang = detect(str(text))
            return lang
        except:
            return 'unknown'
    
    def analyze_comment(self, text: str) -> Dict:
        """Analyze a single comment and return full results"""
        topics = self.detect_topics(text)
        score = self.calculate_kiruna_score(text, topics)
        high_value = self.is_high_value(score, topics)
        delete_recommend = self.get_delete_recommend(topics)
        delete_reason = self.get_delete_reason(topics)
        language = self.detect_language(text)
        
        return {
            'Topic_Tags': ','.join(topics),
            'Kiruna_Score': score,
            'High_Value': high_value,
            'Delete_Recommend': delete_recommend,
            'Delete_Reason': delete_reason,
            'Detected_Language': language
        }


# Main Processing Functions

def process_excel_file(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Process Excel file and add analysis columns
    
    Parameters:
        input_path: input Excel file path
        output_path: output Excel file path
    
    Returns:
        processed DataFrame
    """
    print(f"Reading file: {input_path}")
    df = pd.read_excel(input_path)
    print(f"File loaded, total rows: {len(df)}")
    
    analyzer = KirunaCommentAnalyzer()
    
    print("Analyzing comments...")
    results = []
    
    for idx, row in df.iterrows():
        content = row.get('Content', '')
        result = analyzer.analyze_comment(content)
        results.append(result)
        
        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{len(df)} ({(idx+1)/len(df)*100:.1f}%)")
    
    print("Adding analysis columns...")
    for col in ['Topic_Tags', 'Kiruna_Score', 'High_Value', 'Delete_Recommend', 'Delete_Reason']:
        df[col] = [r[col] for r in results]
    
    print(f"Saving results to: {output_path}")
    df.to_excel(output_path, index=False)
    print("Save completed!")
    
    print_statistics(df)
    
    return df


def print_statistics(df: pd.DataFrame):
    """Print statistical summary"""
    print("\n" + "="*60)
    print("Statistical Summary")
    print("="*60)
    
    total = len(df)
    
    high_value_count = df['High_Value'].sum()
    print(f"\n[High Value Comments]")
    print(f"  High_Value = 1: {high_value_count} ({high_value_count/total*100:.2f}%)")
    print(f"  High_Value = 0: {total - high_value_count} ({(total-high_value_count)/total*100:.2f}%)")
    
    print(f"\n[Kiruna Score Distribution]")
    score_dist = df['Kiruna_Score'].value_counts().sort_index(ascending=False)
    for score, count in score_dist.items():
        print(f"  Score {score}: {count} ({count/total*100:.2f}%)")
    
    print(f"\n[Top Topic Distribution]")
    all_topics = []
    for topics_str in df['Topic_Tags']:
        if pd.notna(topics_str):
            all_topics.extend(str(topics_str).split(','))
    
    from collections import Counter
    topic_counts = Counter(all_topics)
    for topic, count in topic_counts.most_common(10):
        print(f"  {topic}: {count} ({count/total*100:.2f}%)")
    
    delete_count = df['Delete_Recommend'].sum()
    print(f"\n[Deletion Recommendation]")
    print(f"  Delete_Recommend = 1: {delete_count} ({delete_count/total*100:.2f}%)")
    print(f"  Delete_Recommend = 0: {total - delete_count} ({(total-delete_count)/total*100:.2f}%)")
    
    print(f"\n[Deletion Reason Distribution]")
    reason_dist = df[df['Delete_Recommend'] == 1]['Delete_Reason'].value_counts()
    for reason, count in reason_dist.items():
        print(f"  {reason}: {count}")
    
    print("\n" + "="*60)


# Entry Function

if __name__ == '__main__':
    
    INPUT_FILE = 'reply_data_original.xlsx'
    OUTPUT_FILE = 'reply_data_analyzed.xlsx'
    
    df_result = process_excel_file(INPUT_FILE, OUTPUT_FILE)
    
    print(f"\n✅ Processing completed! Results saved to: {OUTPUT_FILE}")
