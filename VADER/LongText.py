# Strategies for Handling Long Texts: 
# For long text content such as articles and reports, sentence segmentation techniques are used for analysis

# from nltk.tokenize import sent_tokenize
# long_text = "THIS IS A LONG TEXT"
 
# sentences = sent_tokenize(long_text)
# for sentence in sentences:
#    vs = analyzer.polarity_scores(sentence)
#    print(f"SENTENCE：{sentence}")
#    print(f"SCORE：{vs['compound']:.2f}")


import nltk
from nltk.tokenize import sent_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Download required NLTK data (runs once, skipped if already present)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

analyzer = SentimentIntensityAnalyzer()

long_text = (
    "Kiruna is a remarkable city in northern Sweden. "
    "The relocation of the entire city is unprecedented in modern history. "
    "Some residents are excited about the new buildings, while others feel sad about leaving their homes."
)

sentences = sent_tokenize(long_text)
for sentence in sentences:
    vs = analyzer.polarity_scores(sentence)
    print(f"Sentence : {sentence}")
    print(f"Score    : {vs['compound']:.2f}")
    print()
