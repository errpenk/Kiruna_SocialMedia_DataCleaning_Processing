analyzer = SentimentIntensityAnalyzer()

sentence = "TEST"
sentiment_scores = analyzer.polarity_scores(sentence)
print(sentiment_scores)
