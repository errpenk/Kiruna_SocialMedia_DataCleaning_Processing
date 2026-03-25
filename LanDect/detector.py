import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Reproducible
DetectorFactory.seed = 0

def detect_language(text):
    """Detecting the language of a single text entry"""
    try:
        if pd.isna(text) or str(text).strip() == "":
            return "unknown"
        return detect(str(text))
    except LangDetectException:
        return "unknown"

def detect_languages_in_file(file_path, text_column, batch_size=500):
    """
    Read a CSV or XLSX file and perform language detection on a specified column

    file_path: File path, supports .csv and .xlsx
    text_column: Column name for which language needs to be detected
    batch_size: Number of rows processed per batch (for progress indication)
    """
    # Read
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Only support .csv and .xlsx ")

    total = len(df)
    print(f"There are {total} records in total. Start detecting the language...")

    results = []
    for i, text in enumerate(df[text_column], 1):
        results.append(detect_language(text))
        if i % batch_size == 0 or i == total:
            print(f"Prograss: {i}/{total}")

    df["detected_lang"] = results

    # Statistics on the number of each language
    lang_counts = df["detected_lang"].value_counts()
    print("\nLanguage distribution：")
    print(lang_counts.to_string())

    # Save
    output_path = file_path.rsplit(".", 1)[0] + "_with_lang.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nSaved: {output_path}")

    return df


df_result = detect_languages_in_file(
    file_path="EXAMPLE_file.xlsx",  
    text_column="content",       
    batch_size=500
)
