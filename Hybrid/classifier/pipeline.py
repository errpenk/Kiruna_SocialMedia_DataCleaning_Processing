"""
pipeline.py
-----------
Orchestrator: calls each module in the correct order and wires their
inputs / outputs together.

Pipeline steps
--------------
  1. cleaner          — load Excel, remove noise rows
  2. language detect  — add Lang_Detected column (optional)
  3. classify         — semantic / LLM / hybrid (controlled by config.MODE)
  4. tag_high_value   — add High_Value column
  5. deletion recs    — add Delete_Recommend / Delete_Reason columns
  6. report + export  — print summary, write output Excel
"""

import pandas as pd

from kiruna_classifier import config
from kiruna_classifier import cleaner
from kiruna_classifier import postprocessor
from kiruna_classifier import reporter


def run(cfg=None) -> pd.DataFrame:
    """
    Execute the full Kiruna classification pipeline.

    Parameters
    ----------
    cfg : module reference (defaults to kiruna_classifier.config).
          Useful for testing with a patched config object.

    Returns
    -------
    Fully processed DataFrame (also written to config.OUTPUT_FILE).
    """
    if cfg is None:
        cfg = config

    _print_header(cfg)

    # ── Step 1: Load and clean ────────────────────────────────────────────
    df, deleted_rows = cleaner.load_and_clean(cfg.INPUT_FILE, cfg.SHEET_NAME)

    # ── Step 2: Language detection (gracefully skipped if not installed) ──
    df = postprocessor.detect_languages(df)

    # ── Step 3: Classification ────────────────────────────────────────────
    mode = cfg.MODE.lower()

    if mode == "semantic":
        from kiruna_classifier import semantic_classifier
        df = semantic_classifier.classify(df)

    elif mode == "llm":
        from kiruna_classifier import llm_classifier
        df = llm_classifier.classify(df)

    elif mode == "hybrid":
        from kiruna_classifier import hybrid_classifier
        df = hybrid_classifier.classify(df)

    else:
        raise ValueError(
            f"Unknown MODE '{cfg.MODE}'. "
            "Valid options: 'semantic', 'llm', 'hybrid'."
        )

    # ── Step 4: High-value tagging ────────────────────────────────────────
    df = postprocessor.tag_high_value(df)

    # ── Step 5: Deletion recommendations ─────────────────────────────────
    df = postprocessor.add_deletion_recommendations(df)

    # ── Step 6: Report and export ─────────────────────────────────────────
    reporter.print_summary(df)
    reporter.export_to_excel(df, deleted_rows, cfg.OUTPUT_FILE)

    return df


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _print_header(cfg) -> None:
    separator = "=" * 60
    print(f"\n{separator}")
    print("  Kiruna Reply Data — Intelligent Classification Pipeline")
    print(f"  Mode : {cfg.MODE.upper()}")
    print(f"  Input: {cfg.INPUT_FILE}")
    print(separator)
