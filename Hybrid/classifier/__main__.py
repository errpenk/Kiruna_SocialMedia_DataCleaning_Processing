"""
__main__.py
-----------
Entry point when the package is executed directly:

    python -m kiruna_classifier

Edit kiruna_classifier/config.py to change mode, thresholds, or file paths
before running.
"""

from kiruna_classifier.pipeline import run

if __name__ == "__main__":
    run()
