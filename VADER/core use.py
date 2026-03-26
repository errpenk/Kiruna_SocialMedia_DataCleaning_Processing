# short using
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

text = "Kiruna's relocation is an incredible feat of urban planning!"
result = analyzer.polarity_scores(text)

print(f"Text   : {text}")
print(f"Result : {result}")
