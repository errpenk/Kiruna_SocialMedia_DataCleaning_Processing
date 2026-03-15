"""
tests/test_postprocessor.py
----------------------------
Unit tests for kiruna_classifier.postprocessor.

Run with:
    pytest tests/test_postprocessor.py -v
"""

import pandas as pd
import pytest
from kiruna_classifier.postprocessor import tag_high_value, add_deletion_recommendations


def _make_df(scores, contents=None):
    """Helper to build a minimal test DataFrame."""
    if contents is None:
        contents = ["sample text"] * len(scores)
    return pd.DataFrame({"CONTENT": contents, "Kiruna_Score": scores})


# ---------------------------------------------------------------------------
# tag_high_value
# ---------------------------------------------------------------------------

class TestTagHighValue:

    def test_high_score_marked_yes(self):
        df = tag_high_value(_make_df([5, 4]))
        assert list(df["High_Value"]) == ["Yes", "Yes"]

    def test_low_score_marked_no(self):
        df = tag_high_value(_make_df([0, 2, 3]))
        assert list(df["High_Value"]) == ["No", "No", "No"]

    def test_mixed_scores(self):
        df = tag_high_value(_make_df([0, 3, 4, 5]))
        assert list(df["High_Value"]) == ["No", "No", "Yes", "Yes"]


# ---------------------------------------------------------------------------
# add_deletion_recommendations
# ---------------------------------------------------------------------------

class TestAddDeletionRecommendations:

    def test_zero_score_short_content_flagged(self):
        df = add_deletion_recommendations(_make_df([0], ["ab"]))
        assert df.at[0, "Delete_Recommend"] == "Yes"

    def test_advertisement_flagged(self):
        df = add_deletion_recommendations(_make_df([3], ["Visit http://spam.com"]))
        assert df.at[0, "Delete_Recommend"] == "Yes"

    def test_high_score_not_flagged(self):
        df = add_deletion_recommendations(_make_df([5], ["The church was relocated."]))
        assert df.at[0, "Delete_Recommend"] == "No"

    def test_zero_score_long_content_not_flagged(self):
        # Zero score but content is >= 8 chars — do not recommend deletion
        df = add_deletion_recommendations(_make_df([0], ["This is a long enough comment"]))
        assert df.at[0, "Delete_Recommend"] == "No"
