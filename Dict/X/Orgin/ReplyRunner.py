import pandas as pd
import re
import numpy as np
from langdetect import detect, DetectorFactory
from typing import List, Dict, Tuple, Optional
from collections import Counter

# Set random seed to ensure reproducible results
# DetectorFactory.seed = 42

# Configuration Class

class Config:
    """Configuration class - all keywords, rules, and parameters are defined here"""
    
    # Core Relevant Topic Keywords 
    
    # Kiruna_Relocation (Score 5)
    KIRUNA_RELOCATION = {
        'must_have': ['kiruna'],
        'any_of': ['relocation', 'relocating', 'moving', 'town', 'flytt', 'flytta', 'flyttar']
    }
    
    # Kiruna_Mining (Score 5)
    KIRUNA_MINING = {
        'must_have': ['kiruna'],
        'any_of': ['mining', 'mine', 'lkab', 'iron ore', 'malm', 'gruva']
    }
    
    # Kiruna_LocalLife (Score 5)
    KIRUNA_LOCALLIFE = {
        'must_have': ['kiruna'],
        'any_of': ['badhus', 'pool', 'daily', 'life', 'nybyggt']
    }
    
    # Mining_Mineral (Score 5)
    MINING_MINERAL = {
        'any_of': ['mining', 'mine', 'iron ore', 'iron-ore', 'malm', 'gruva', 'mineral', 'ore'],
        'exclude': ['game', 'minecraft', 'video game']  # Exclude game-related content
    }
    
    # Sami_Indigenous (Score 4)
    SAMI_INDIGENOUS = {
        'any_of': ['sámi', 'sami', 'lappland', 'norrland', 'indigenous', 'same']
    }
    
    # Engineering_Reaction (Score 4)
    ENGINEERING_REACTION = {
        'any_of': ['lift', 'how did', "how'd", 'engineering', 'technical', 'move it', 'moving it']
    }
    
    # Church_Relocation (Score 5)
    CHURCH_RELOCATION = {
        'any_of': ['church', 'moving church', 'dismantl', '600-ton', '672-ton', 'intact'],
        'must_have_context': ['move', 'moving', 'relocat']
    }
    
    # ========== Secondary Relevant Topic Keywords ==========
    
    # Engineering_Move (Score 3)
    ENGINEERING_MOVE = {
        'any_of': ['mammoet', '1250 tonnes', '1250 tons', '600-ton', '672-ton', 'engineering', 
                   'moved it', 'moving it', 'wheels', 'beams', 'trailers']
    }
    
    # Cultural_Heritage (Score 3)
    CULTURAL_HERITAGE = {
        'any_of': ['heritage', 'cultural', 'preserve', 'history', 'historical', 'preservation']
    }
    
    # Religious_Discussion (Score 3)
    RELIGIOUS_DISCUSSION = {
        'any_of': ['church', 'religion', 'faith', 'god', 'jesus', 'kyrkan', 'kyrka'],
        'exclude': ['burn', 'muslim', 'mosque', 'trump']  # Exclude sensitive content
    }
    
    # Sweden_General (Score 2)
    SWEDEN_GENERAL = {
        'any_of': ['sweden', 'swedish', "sweden's"],
        'must_not_have': ['kiruna']  # If Kiruna is present, classify as a core topic
    }
    
    # Distance_Location (Score 3)
    DISTANCE_LOCATION = {
        'any_of': ['km', 'kilometers', 'kilometres', 'miles', '5 km', 'five kilometers', 
                   'new location', 'away from']
    }
    
    # Weight_Size (Score 4)
    WEIGHT_SIZE = {
        'any_of': ['tonnes', 'tons', '600', '1250', '672', 'heavy', 'massive', 'large'],
        'must_have_context': ['church', 'building', 'move', 'weight']
    }
    
    # Time_Age (Score 3)
    TIME_AGE = {
        'any_of': ['years old', 'year-old', 'century', 'old', 'historic', '1900', '113-year']
    }
    
    # Emotion / Reaction Topic Keywords
    
    # Positive_Reaction (Score 2)
    POSITIVE_REACTION = {
        'any_of': ['amazing', 'incredible', 'awesome', 'impressive', 'fascinating', 
                   'love', 'great', 'fantastic', 'remarkable', 'cool']
    }
    
    # Negative_Reaction (Score 1)
    NEGATIVE_REACTION = {
        'any_of': ['waste', 'unnecessary', 'crazy', 'ridiculous', 'stupid', 'foolish', 'bad'],
        'exclude': ['muslim', 'burn', 'trump']  # Exclude sensitive content
    }
    
    # Neutral_Observation (Score 2)
    NEUTRAL_OBSERVATION = {
        'any_of': ['interesting', 'i see', 'looks like', 'seems', 'appears', 'i think', 'i believe']
    }
    
    # Question_Curiosity (Score 2)
    QUESTION_CURIOSITY = {
        'any_of': ['@grok', '@gpt', 'what', 'how', 'why', 'when', 'where', 'question', 
                   'wonder', 'can you help', 'kan du hjälpa']
    }
    
    # Comparison (Score 2)
    COMPARISON = {
        'any_of': ['like', 'similar to', 'compared to', 'just like', 'as if', 'reminds me of', 
                   'unlike', 'than']
    }
    
    # Short_Reaction (Score 1)
    SHORT_REACTION = {
        'exact_match': ['wow', 'interesting', 'insane', 'cool', 'nice', 'good one', 'awesome', 
                        'amazing', 'wow!', 'interesting!', 'insane!']
    }
    
    # Low-quality Content Keywords
    
    # Political_Sensitive (Delete)
    POLITICAL_SENSITIVE = {
        'any_of': ['trump', 'muslims', 'muslim', 'burn', 'mosque', 'asylum seekers',
                   'mohammed', '3rd world', 'immigrants', 'bränn alla kyrkor', 
                   'ukraina', 'palestine', 'gaza'],
        'negative_context': ['burn', 'before', 'hope', 'not', 'won\'t', 'will', 'should']
    }
    
    # Off_Topic_Complete (Delete)
    OFF_TOPIC_LOCATIONS = {
        'any_of': ['kenya', 'kisumu', 'nairobi', 'turkey', 'tel aviv', 'palestine',
                   'gaza', 'ukraine', 'hasankeyf'],
        'must_not_have': ['sweden', 'swedish', 'kiruna', 'like', 'similar']  # Exclude comparison context
    }
    
    # Emoji Regex
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )


# Core Analysis Class

class KirunaCommentAnalyzer:
    """Kiruna Comment Analyzer - Professional Data Analyst Version"""
    
    def __init__(self):
        self.config = Config()
        self.topic_counts = Counter()
    
    def is_empty_or_meaningless(self, text: str) -> bool:
        """Check whether the content is empty or meaningless"""
        if pd.isna(text) or text is None:
            return True
        
        text = str(text).strip()
        
        if len(text) == 0:
            return True
        
        if text.isspace():
            return True
        
        # Punctuation only
        if re.match(r'^[\W_]+$', text):
            return True
        
        # Emojis only
        text_no_emoji = self.config.EMOJI_PATTERN.sub('', text)
        if len(text_no_emoji.strip()) == 0:
            return True
        
        return False
    
    def is_political_sensitive(self, text: str) -> bool:
        """Check whether the content contains political/religious sensitive topics"""
        if pd.isna(text):
            return False
        
        text_lower = str(text).lower()
        
        for keyword in self.config.POLITICAL_SENSITIVE['any_of']:
            if keyword.lower() in text_lower:
                # Check whether it appears in a negative context
                if any(ctx in text_lower for ctx in ['burn', 'muslim', 'mosque', 'trump', 'ukraina', 'palestine']):
                    return True
                # Some keywords are directly classified as sensitive
                if keyword.lower() in ['trump', '3rd world', 'asylum seekers']:
                    return True
        
        return False
    
    def is_off_topic_location(self, text: str) -> bool:
        """Check whether the comment refers to completely unrelated locations"""
        if pd.isna(text):
            return False
        
        text_lower = str(text).lower()
        
        # Check unrelated locations
        for location in self.config.OFF_TOPIC_LOCATIONS['any_of']:
            if location.lower() in text_lower:
                # Check whether there is Sweden/Kiruna context or comparison context
                has_sweden_context = any(
                    kw in text_lower for kw in ['sweden', 'swedish', 'kiruna', 'like', 'similar', 'compared']
                )
                if not has_sweden_context:
                    return True
        
        return False
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the comment"""
        if pd.isna(text) or len(str(text).strip()) < 10:
            return 'unknown'
        
        try:
            lang = detect(str(text))
            return lang
        except:
            return 'unknown'
    
    def has_keywords(self, text_lower: str, config: Dict) -> bool:
        """Check whether the text contains keywords defined in the configuration"""
        # Check required words
        if 'must_have' in config:
            if not any(kw in text_lower for kw in config['must_have']):
                return False
        
        # Check forbidden words
        if 'must_not_have' in config:
            if any(kw in text_lower for kw in config['must_not_have']):
                return False
        
        # Check any matching word
        if 'any_of' in config:
            if not any(kw in text_lower for kw in config['any_of']):
                return False
        
        # Check excluded words
        if 'exclude' in config:
            if any(kw in text_lower for kw in config['exclude']):
                return False
        
        # Check exact match
        if 'exact_match' in config:
            if text_lower.strip() not in [kw.lower() for kw in config['exact_match']]:
                if not any(kw.lower() in text_lower for kw in config['exact_match']):
                    return False
        
        # Check context requirement
        if 'must_have_context' in config:
            if not any(kw in text_lower for kw in config['must_have_context']):
                return False
        
        return True
    
    def detect_topics(self, text: str) -> List[str]:
        """Detect topic tags in the comment (multi-label supported)"""
        if pd.isna(text):
            return ['Empty_Meaningless']
        
        text_lower = str(text).lower()
        topics = []
        
        # Priority 1: Empty / meaningless
        if self.is_empty_or_meaningless(text):
            return ['Empty_Meaningless']
        
        # Priority 2: Sensitive content
        if self.is_political_sensitive(text):
            return ['Political_Sensitive']
        
        # Priority 3: Completely unrelated geography
        if self.is_off_topic_location(text):
            return ['Off_Topic_Complete']
        
        # Priority 4: Core relevant topics (Score 4-5)
        if self.has_keywords(text_lower, self.config.KIRUNA_RELOCATION):
            topics.append('Kiruna_Relocation')
        
        if self.has_keywords(text_lower, self.config.KIRUNA_MINING):
            topics.append('Kiruna_Mining')
        
        if self.has_keywords(text_lower, self.config.KIRUNA_LOCALLIFE):
            topics.append('Kiruna_LocalLife')
        
        if self.has_keywords(text_lower, self.config.MINING_MINERAL):
            topics.append('Mining_Mineral')
        
        if self.has_keywords(text_lower, self.config.SAMI_INDIGENOUS):
            topics.append('Sami_Indigenous')
        
        if self.has_keywords(text_lower, self.config.ENGINEERING_REACTION):
            topics.append('Engineering_Reaction')
        
        if self.has_keywords(text_lower, self.config.CHURCH_RELOCATION):
            topics.append('Church_Relocation')
        
        # Priority 5: Secondary relevant topics (Score 2-3)
        if self.has_keywords(text_lower, self.config.ENGI
