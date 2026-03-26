import sys
import subprocess


def install_if_missing(package, import_name=None):
    import importlib
    try:
        importlib.import_module(import_name or package)
    except ImportError:
        print(f"{package} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])


# Automatically install dependencies
for pkg, imp in [
    ("vaderSentiment", "vaderSentiment"),
    ("langdetect", "langdetect"),
    ("deep-translator","deep_translator"),
    ("openpyxl", "openpyxl"),
    ("tqdm", "tqdm"),
]:
    install_if_missing(pkg, imp)

# import
import config
from loader import load_input
from translator import detect_and_translate
from sentiment import run_vader
from exporter import save_results


def main():
    print(f"\n{'='*55}")
    print("VADER Sentiment Analysis — Multilingual Automatic Detection + Translation")
    print(f"{'='*55}\n")

    # 1. load
    print(f"load：{config.INPUT_FILE}")
    df = load_input(config.INPUT_FILE)
    print(f" {len(df):,} rows | columns: {list(df.columns)}")

    if config.TEXT_COLUMN not in df.columns:
        raise KeyError(
            f"cannot find column '{config.TEXT_COLUMN}'，please check config.py - TEXT_COLUMN \n"
            f"currently column：{list(df.columns)}"
        )

    # 2. Language detection & translation
    print("\n Language detection & translation ...")
    df = detect_and_translate(df, config.TEXT_COLUMN)

    # 3. VADER
    print("VADER analysis ...")
    df = run_vader(df)

    # 4. export
    print(f"\n[export to：{config.OUTPUT_FILE}")
    save_results(df, config.OUTPUT_FILE)

    # summary
    print("\ndistribution")
    print(df["sentiment_label"].value_counts().to_string())
    print("\nstat")
    print(df["vader_compound"].describe().round(4).to_string())
    print()


if __name__ == "__main__":
    main()
