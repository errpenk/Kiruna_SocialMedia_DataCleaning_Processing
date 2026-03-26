
# Data loading, classification, and export for Kiruna reply data

import pandas as pd
from collections import Counter
from reply_classifier import classify_reply
from reply_keywords import KEEP_SCORE_THRESHOLD


def load_data(file_path: str, sheet_name: str = "reply data") -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Loaded {len(df):,} rows from sheet '{sheet_name}'")
    return df


def save_data(df: pd.DataFrame, file_path: str) -> None:
    df.to_excel(file_path, index=False)
    print(f"Saved {len(df):,} rows to {file_path}")


def run_pipeline(
    df: pd.DataFrame,
    content_col: str = "Title/Description",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply the classifier to every row and split into kept and deleted sets.

    df_kept: rows with Kiruna_Score >= KEEP_SCORE_THRESHOLD
    df_deleted: rows below threshold, with score and deletion reason columns
    """
    scores, decisions, topics_list, reasons = [], [], [], []

    for text in df[content_col]:
        score, decision, topics, reason = classify_reply(text)
        scores.append(score)
        decisions.append(decision)
        topics_list.append(", ".join(topics) if topics else "")
        reasons.append(reason)

    df = df.copy()
    df["Kiruna_Score"] = scores
    df["Keep_Delete"] = decisions
    df["Matched_Topics"] = topics_list
    df["Delete_Reason"]  = reasons

    df_kept = (
        df[df["Keep_Delete"] == "KEEP"]
        .drop(columns=["Keep_Delete", "Delete_Reason"])
        .reset_index(drop=True)
    )

    df_deleted = (
        df[df["Keep_Delete"] == "DELETE"]
        .drop(columns=["Keep_Delete"])
        .reset_index(drop=True)
    )

    return df_kept, df_deleted


def print_report(df_orig: pd.DataFrame, df_kept: pd.DataFrame, df_deleted: pd.DataFrame) -> None:
    total = len(df_orig)
    n_kept = len(df_kept)
    n_del = len(df_deleted)

    print("\n" + "=" * 60)
    print(f"Total replies: {total:>6,}")
    print(f"Kept (score >= {KEEP_SCORE_THRESHOLD}): {n_kept:>6,}  ({n_kept/total * 100:.1f}%)")
    print(f"Deleted (score < {KEEP_SCORE_THRESHOLD}): {n_del:>6,}  ({n_del/total * 100:.1f}%)")
    print("=" * 60)

    print("\n  Score distribution (kept)")
    score_counts = df_kept["Kiruna_Score"].value_counts().sort_index(ascending=False)
    for score, count in score_counts.items():
        bar = "#" * min(count, 40)
        print(f"Score {score}  {count:>5,}  {bar}")

    print("\n  Deletion breakdown")
    reason_counts = df_deleted["Delete_Reason"].value_counts()
    for reason, count in reason_counts.items():
        print(f"{reason:<40} {count:>5,}")

    print("\n  Top matched topics (kept)")
    all_topics: list[str] = []
    for cell in df_kept["Matched_Topics"]:
        if cell:
            all_topics.extend([t.strip() for t in cell.split(",")])
    topic_counts = Counter(all_topics).most_common(10)
    for topic, count in topic_counts:
        print(f"{topic:<35} {count:>5,}")

    print()
