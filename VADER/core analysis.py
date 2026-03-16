# pip install vaderSentiment openpyxl pandas
# git clone https://gitcode.com/gh_mirrors/va/vaderSentiment

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()
df = pd.read_excel('KIRUNA EXAMPLE.xlsx') # EXAMPLE


# Could change the score scope to 0-5
def get_sentiment(text):
    if pd.isna(text) or str(text).strip() == '':
        return 'Neutral', 0.0
    scores = analyzer.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:   
        return 'Positive', compound
    elif compound <= -0.05: 
        return 'Negative', compound
    else:                   
        return 'Neutral',  compound

df[['sentiment', 'compound']] = df['CONTENT'].apply(
    lambda x: pd.Series(get_sentiment(x))
)

print(df['sentiment'].value_counts())
