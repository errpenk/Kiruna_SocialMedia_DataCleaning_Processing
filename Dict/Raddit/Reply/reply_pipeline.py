
# Data loading, enrichment, and export for Kiruna reply data
# Output keeps all rows in one sheet, with added annotation columns

import pandas as pd
from collections import Counter
from reply_classifier import classify_reply
from reply_keywords import KEEP_SCORE_THRESHOLD


def load_data(file_path: str, sheet_name: str = "reply data") -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df["CONTENT"] = df["CONTENT"].fillna("").astype(str)
    print(f"Loaded {len(df):,} rows from sheet '{sheet_name}'")
    return df


def save_data(df_annotated: pd.DataFrame, df_deleted: pd.DataFrame, output_file: str) -> None:
    """Save annotated (kept) rows and deleted rows to two sheets in one XLSX."""
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_annotated.to_excel(writer, sheet_name="reply data", index=False)
        df_deleted.to_excel(writer, sheet_name="deleted", index=False)
    print(f"Saved to {output_file}")
    print(f"Sheet 'reply data' : {len(df_annotated):,} rows")
    print(f"Sheet 'deleted' : {len(df_deleted):,} rows")


def run_pipeline(
    df: pd.DataFrame,
    content_col: str = "CONTENT",
) -> tuple:
    """
    Annotate every row; return (df_annotated, df_deleted).

    df_annotated : rows that passed the initial noise filter, with topic/score columns
    df_deleted   : rows removed during initial cleaning, with deletion reasons
    """
    keeps, initial_reasons, topics, scores, high_values, recs, final_reasons = (
        [], [], [], [], [], [], []
    )

    for content in df[content_col]:
        keep, init_r, topic, score, hv, rec, fin_r = classify_reply(content)
        keeps.append(keep)
        initial_reasons.append(init_r)
        topics.append(topic)
        scores.append(score)
        high_values.append(hv)
        recs.append(rec)
        final_reasons.append(fin_r)

    df = df.copy()
    df["_keep"] = keeps
    df["_initial_reason"] = initial_reasons
    df["Kiruna_Topic"] = topics
    df["Kiruna_Score"] = scores
    df["High_Value"] = high_values
    df["Delete_Recommend"] = recs
    df["Delete_Reason"] = final_reasons

    df_deleted = (
        df[~df["_keep"]]
        .rename(columns={"_initial_reason": "Delete_Reason_Initial"})
        .drop(columns=["_keep"])
        .reset_index(drop=True)
    )

    df_annotated = (
        df[df["_keep"]]
        .drop(columns=["_keep", "_initial_reason"])
        .reset_index(drop=True)
    )

    return df_annotated, df_deleted


def print_report(
    df_orig: pd.DataFrame,
    df_annotated: pd.DataFrame,
    df_deleted: pd.DataFrame,
) -> None:
    total  = len(df_orig)
    n_kept = len(df_annotated)
    n_del  = len(df_deleted)

    print("\n" + "=" * 60)
    print(f"Total replies: {total:>6,}")
    print(f"After initial cleaning: {n_kept:>6,}  ({n_kept / total * 100:.1f}%)")
    print(f"Removed in initial cleaning: {n_del:>6,}  ({n_del / total * 100:.1f}%)")
    print("=" * 60)

    print("\n  Score distribution (kept rows)")
    score_counts = df_annotated["Kiruna_Score"].value_counts().sort_index(ascending=False)
    for score, count in score_counts.items():
        bar = "#" * min(count, 40)
        print(f"Score {score}  {count:>5,}  {bar}")

    high = (df_annotated["High_Value"] == "Yes").sum()
    above = (df_annotated["Kiruna_Score"] >= KEEP_SCORE_THRESHOLD).sum()
    print(f"\nHigh-value rows (score >= 4): {high:>6,}")
    print(f"Rows with score >= {KEEP_SCORE_THRESHOLD}: {above:>6,}")

    print("\nTopic distribution (kept rows)")
    for topic, count in df_annotated["Kiruna_Topic"].value_counts().items():
        print(f"{topic:<35} {count:>5,}")

    print("\nInitial deletion breakdown")
    for reason, count in df_deleted["Delete_Reason_Initial"].value_counts().items():
        print(f"{reason:<40} {count:>5,}")
    print()
