# short using
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
 
analyzer = SentimentIntensityAnalyzer()
text = "TEXT"
result = analyzer.polarity_scores(text)
 
print(f"RESULT：{result}")
