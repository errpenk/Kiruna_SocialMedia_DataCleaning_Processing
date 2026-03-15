"""
kiruna_classifier
-----------------
Package for cleaning and classifying Kiruna-related Reddit reply data.

Quick usage
-----------
    from kiruna_classifier import run
    df = run()

Or from the command line:
    python -m kiruna_classifier
"""

from kiruna_classifier.pipeline import run

__all__ = ["run"]
