"""
Parallel language detection using ThreadPoolExecutor
Use this as a drop-in replacement for the loop in detector.py when processing large files (typically 5 000+ rows)
"""

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

DetectorFactory.seed = 0


def detect_language(text) -> str:
    try:
        if pd.isna(text) or str(text).strip() == "":
            return "unknown"
        return detect(str(text))
    except LangDetectException:
        return "unknown"


if __name__ == "__main__":
    file_path    = "Kiruna_file.xlsx"   # change
    text_column  = "content"           # change
    max_workers  = 4                   # change

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    print(f"Loaded {len(df):,} rows. Running parallel detection with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(detect_language, df[text_column]))

    df["detected_lang"] = results

    print("\nLanguage distribution:")
    print(df["detected_lang"].value_counts().to_string())

    output_path = file_path.rsplit(".", 1)[0] + "_with_lang.xlsx"
    df.to_excel(output_path, index=False)
    print(f"\nSaved: {output_path}")
