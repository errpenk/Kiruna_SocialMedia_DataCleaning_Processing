# VADER
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def _scores(text: str, analyzer: SentimentIntensityAnalyzer) -> dict:
    """Returns a VADER four-score for a single text"""
    if not text or not str(text).strip():
        return {"neg": None, "neu": None, "pos": None, "compound": None}
    return analyzer.polarity_scores(str(text))


def classify(compound) -> str:
    """Return the sentiment label based on the compound value"""
    if compound is None:
        return "N/A"
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def run_vader(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform VADER analysis on df['text_for_vader']
    Add the following columns: vader_neg, vader_neu, vader_pos, vader_compound, and sentiment_label
    """
    analyzer = SentimentIntensityAnalyzer()
    results = df["text_for_vader"].apply(lambda t: _scores(t, analyzer))

    df["vader_neg"] = results.apply(lambda x: x["neg"])
    df["vader_neu"] = results.apply(lambda x: x["neu"])
    df["vader_pos"] = results.apply(lambda x: x["pos"])
    df["vader_compound"] = results.apply(lambda x: x["compound"])
    df["sentiment_label"] = df["vader_compound"].apply(classify)
    return df
