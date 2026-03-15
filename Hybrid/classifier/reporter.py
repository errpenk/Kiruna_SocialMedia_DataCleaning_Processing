"""
reporter.py
-----------
Final pipeline step: print a summary to the console and export results
to an Excel workbook with two sheets:

  Sheet 1 "reply data"   — cleaned and classified comments
  Sheet 2 "deleted_log"  — rows removed during the initial cleaning step
"""

import pandas as pd
from typing import Dict, List


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

def print_summary(df: pd.DataFrame) -> None:
    """Print a compact classification summary to stdout."""
    total      = len(df)
    related    = (df["Kiruna_Related"] == "Yes").sum()    if "Kiruna_Related"    in df.columns else "N/A"
    high_value = (df["High_Value"]     == "Yes").sum()    if "High_Value"        in df.columns else "N/A"
    to_delete  = (df["Delete_Recommend"] == "Yes").sum()  if "Delete_Recommend"  in df.columns else "N/A"

    separator = "=" * 52
    print(f"\n{separator}")
    print("  Classification Summary")
    print(separator)
    print(f"  Total rows             : {total}")
    print(f"  Kiruna-related         : {related}")
    print(f"  High-value (score ≥ 4) : {high_value}")
    print(f"  Recommended for delete : {to_delete}")

    if "Kiruna_Topic" in df.columns:
        print("\n  Topic distribution:")
        for topic, count in df["Kiruna_Topic"].value_counts().items():
            print(f"    {topic:<28} {count}")

    if "Lang_Detected" in df.columns:
        print("\n  Top 10 detected languages:")
        for lang, count in df["Lang_Detected"].value_counts().head(10).items():
            print(f"    {lang:<10} {count}")

    print(separator)


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

def export_to_excel(
    df: pd.DataFrame,
    deleted_rows: List[Dict],
    output_file: str,
) -> None:
    """
    Write the classified DataFrame and the deletion log to an Excel workbook.

    Parameters
    ----------
    df           : fully processed DataFrame
    deleted_rows : list of dicts produced by the cleaner step
    output_file  : destination file path (e.g. "kiruna_reply_data_cleaned.xlsx")
    """
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="reply data", index=False)

        if deleted_rows:
            pd.DataFrame(deleted_rows).to_excel(
                writer, sheet_name="deleted_log", index=False
            )

    print(f"\n[Reporter] Output saved to: {output_file}")
    print(f"[Reporter] Columns written: {list(df.columns)}")
