import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



INPUT_FILE = "KIRUNA_DATA.xlsx"    
OUTPUT_FILE = "KIRUNA_VADER_RESULTS.xlsx"

TEXT_COLUMN = "CONTENT"

# standard VADER compound-score thresholds
POSITIVE_THRESHOLD = 0.05
NEGATIVE_THRESHOLD = -0.05


# load
def load_data(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. Please use CSV, XLSX, or XLS."
        )

    return df


df = load_data(INPUT_FILE)


# check if the specified text column exists in the dataset

if TEXT_COLUMN not in df.columns:
    raise ValueError(
        f"Column '{TEXT_COLUMN}' not found in the dataset.\n"
        f"Available columns: {list(df.columns)}"
    )


# initialize VADER
analyzer = SentimentIntensityAnalyzer()



# sentiment analysis function

def analyze_sentiment(text):
    # Handle missing or empty values
    if pd.isna(text):
        return pd.Series({
            "vader_neg": None,
            "vader_neu": None,
            "vader_pos": None,
            "vader_compound": None,
            "sentiment": "Unknown"
        })

    text = str(text).strip()

    if text == "":
        return pd.Series({
            "vader_neg": None,
            "vader_neu": None,
            "vader_pos": None,
            "vader_compound": None,
            "sentiment": "Unknown"
        })

    # run VADER
    scores = analyzer.polarity_scores(text)

    compound = scores["compound"]

    # standard VADER classification
    if compound >= POSITIVE_THRESHOLD:
        sentiment = "Positive"

    elif compound <= NEGATIVE_THRESHOLD:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return pd.Series({
        "vader_neg": scores["neg"],
        "vader_neu": scores["neu"],
        "vader_pos": scores["pos"],
        "vader_compound": compound,
        "sentiment": sentiment
    })



# apply sentiment analysis to the dataset
sentiment_results = df[TEXT_COLUMN].apply(analyze_sentiment)

df = pd.concat(
    [df, sentiment_results],
    axis=1
)



# summary
print("VADER SENTIMENT DISTRIBUTION")
print(
    df["sentiment"]
    .value_counts(dropna=False)
)



print("VADER SENTIMENT PERCENTAGES")
percentages = (
    df["sentiment"]
    .value_counts(normalize=True, dropna=False)
    .mul(100)
    .round(2)
)

print(percentages)


print("COMPOUND SCORE SUMMARY")

print(
    df["vader_compound"]
    .describe()
)



# save results
extension = os.path.splitext(OUTPUT_FILE)[1].lower()

if extension == ".csv":
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

elif extension in [".xlsx", ".xls"]:
    df.to_excel(
        OUTPUT_FILE,
        index=False
    )

else:
    raise ValueError(
        "Output file must be CSV, XLSX, or XLS."
    )


print(
    f"\nAnalysis complete.\n"
    f"Results saved to: {OUTPUT_FILE}"
)