"""
tests/test_cleaner.py
---------------------
Unit tests for kiruna_classifier.cleaner.

Run with:
    pytest tests/test_cleaner.py -v
"""

import pytest
from kiruna_classifier.cleaner import (
    _is_empty_or_punctuation_only,
    _is_advertisement,
    _is_structurally_meaningless,
    _is_too_short_to_be_useful,
)


# ---------------------------------------------------------------------------
# _is_empty_or_punctuation_only
# ---------------------------------------------------------------------------

class TestEmptyOrPunctuationOnly:

    def test_empty_string(self):
        assert _is_empty_or_punctuation_only("") is True

    def test_whitespace_only(self):
        assert _is_empty_or_punctuation_only("   ") is True

    def test_punctuation_only(self):
        assert _is_empty_or_punctuation_only("...!!!???") is True

    def test_normal_text(self):
        assert _is_empty_or_punctuation_only("This is a comment") is False

    def test_single_word(self):
        assert _is_empty_or_punctuation_only("wow") is False


# ---------------------------------------------------------------------------
# _is_advertisement
# ---------------------------------------------------------------------------

class TestIsAdvertisement:

    def test_http_url(self):
        assert _is_advertisement("Check this out http://spam.com") is True

    def test_https_url(self):
        assert _is_advertisement("Visit https://example.com for deals") is True

    def test_www_url(self):
        assert _is_advertisement("Go to www.example.com") is True

    def test_discount_word(self):
        assert _is_advertisement("Get a huge discount today!") is True

    def test_normal_comment(self):
        assert _is_advertisement("The mine in Kiruna is fascinating.") is False


# ---------------------------------------------------------------------------
# _is_structurally_meaningless
# ---------------------------------------------------------------------------

class TestIsStructurallyMeaningless:

    def test_lone_mention(self):
        assert _is_structurally_meaningless("@username") is True

    def test_lone_hashtag(self):
        assert _is_structurally_meaningless("#kiruna") is True

    def test_crosses_only(self):
        assert _is_structurally_meaningless("✝✝✝") is True

    def test_normal_text(self):
        assert _is_structurally_meaningless("Amazing place to visit!") is False

    def test_mention_with_text(self):
        # Mention followed by actual content should NOT be flagged
        assert _is_structurally_meaningless("@user great point!") is False


# ---------------------------------------------------------------------------
# _is_too_short_to_be_useful
# ---------------------------------------------------------------------------

class TestIsTooShort:

    def test_very_short_meaningless(self):
        assert _is_too_short_to_be_useful("ab") is True

    def test_short_but_meaningful_word(self):
        assert _is_too_short_to_be_useful("wow") is False

    def test_emoticon_kept(self):
        assert _is_too_short_to_be_useful(":)") is False

    def test_long_enough(self):
        assert _is_too_short_to_be_useful("looong") is False
