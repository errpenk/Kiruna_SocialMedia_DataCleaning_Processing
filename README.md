# Kiruna Media Data — Analysis & Visualization

A Python toolkit for collecting, cleaning, and analysing the Kiruna media corpus. The project is organised into five independent modules that follow a natural data pipeline — from raw data cleaning through language detection, sentiment scoring, and semantic embedding.

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Repository Structure](#repository-structure)
3. [Module 1 — Post Data Cleaning](#module-1--post-data-cleaning)
4. [Module 2 — Reply Data Cleaning](#module-2--reply-data-cleaning)
5. [Module 3 — Language Detection](#module-3--language-detection)
6. [Module 4 — Sentiment Analysis (VADER)](#module-4--sentiment-analysis-vader)
7. [Module 5 — Semantic Embedding](#module-5--semantic-embedding)
8. [Requirements](#requirements)

---

## Pipeline Overview

```
Raw Data (.xlsx / .csv)
        │
        ▼
┌───────────────────┐     ┌───────────────────┐
│  Module 1         │     │  Module 2         │
│  Post Cleaning    │     │  Reply Cleaning   │
│  3-label filter   │     │  0–5 score filter │
└────────┬──────────┘     └────────┬──────────┘
         │                         │
         └──────────┬──────────────┘
                    ▼
          ┌─────────────────┐
          │   Module 3      │
          │ Language Detect │
          └────────┬────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────┐
│   Module 4      │  │   Module 5          │
│ Sentiment (VADER│  │ Semantic Embedding  │
│ + Translation)  │  │ Similarity/Cluster  │
└─────────────────┘  └─────────────────────┘
```

Each module can also be used independently on any CSV or XLSX file.

---

## Repository Structure

```
kiruna-media-data/
│
├── post_filter/                    # Module 1 — Post cleaning & classification
│   ├── Main.py                     # Entry point
│   ├── Pipeline.py                 # Load → classify → export
│   ├── Classifier.py               # 3-label classifier (direct / indirect / irrelevant)
│   └── Keywords.py                 # Keyword lists and spam filters
│
├── reply_filter/                   # Module 2 — Reply cleaning & scoring
│   ├── main.py                     # Entry point
│   ├── reply_pipeline.py           # Load → score → export
│   ├── reply_classifier.py         # Score-based classifier (0–5)
│   └── reply_keywords.py           # Keyword lists and score definitions
│
├── lang_detection/                 # Module 3 — Language detection
│   ├── detector.py                 # Main detection script (batch + progress)
│   └── LanBatch.py                 # Parallel detection (ThreadPoolExecutor)
│
├── vader_sentiment/                # Module 4 — Sentiment analysis
│   ├── main.py                     # Entry point for the full pipeline
│   ├── config.py                   # Input / output / column configuration
│   ├── loader.py                   # CSV / XLSX reader with auto encoding detection
│   ├── translator.py               # Language detection + Google Translate
│   ├── sentiment.py                # VADER scoring and labelling
│   ├── exporter.py                 # Formatted XLSX export
│   ├── core_use.py                 # Minimal single-text example
│   ├── instantiation.py            # Basic VADER instantiation example
│   ├── monitor.py                  # Batch comment analysis example
│   └── long_text.py                # Sentence-level analysis for long texts
│
└── semantic_embedding/             # Module 5 — Semantic embedding & clustering
    ├── BasicEmbedding.py           # Generate sentence embeddings
    ├── CalSim.py                   # Cosine similarity between sentences
    ├── TextCluster.py              # K-Means clustering on embeddings
    └── MultLinModel.py             # Batch encoding for large multilingual corpora
```

---

## Module 1 — Post Data Cleaning

Classifies raw posts into three relevance categories using keyword matching and spam filters. Outputs separate files for each category.

### Classification Labels

| Label | Meaning |
|---|---|
| `1` | Directly related — Kiruna explicitly mentioned |
| `2` | Indirectly related — background topics (mining, relocation, Sámi culture, etc.) |
| `0` | Irrelevant — deleted |

### Run

```bash
python Main.py \
  --input           kiruna_posts.xlsx \
  --sheet           "post data" \
  --col             "Title/Description" \
  --output-class1   kiruna_class1_direct.xlsx \
  --output-class2   kiruna_class2_indirect.xlsx \
  --output-deleted  kiruna_deleted.xlsx \
  --output-combined kiruna_posts_cleaned.xlsx
```

### Output

The script prints a classification report and saves four files: directly related, indirectly related, deleted (with reasons), and a combined clean dataset.

> Edit `Keywords.py` to add or remove keywords for any category.

---

## Module 2 — Reply Data Cleaning

Scores each reply from 0 to 5 based on topic relevance. Replies below the threshold are filtered out and saved separately with deletion reasons.

### Scoring Schema

| Score | Topic |
|---|---|
| `5` | Church / city relocation |
| `4` | Mining, Sámi culture, aerospace, northern Swedish life |
| `3` | Place names, climate, tourism |
| `2` | General Nordic / Swedish culture |
| `1` | Edge mentions |
| `0` | Irrelevant / noise — deleted |

Default keep threshold: **score ≥ 3** (configurable via `KEEP_SCORE_THRESHOLD` in `reply_keywords.py`).

### Run

```bash
python main.py \
  --input          kiruna_replies.xlsx \
  --sheet          "reply data" \
  --col            "Title/Description" \
  --output-kept    kiruna_replies_kept.xlsx \
  --output-deleted kiruna_replies_deleted.xlsx
```

### Output

Each kept reply receives `Kiruna_Score`, `Matched_Topics`, and a `High_Value` flag (score ≥ 4). Deleted replies are saved with their deletion reason.

---

## Module 3 — Language Detection

Detects the language of every text entry in a CSV or XLSX file and appends a `detected_lang` column. Supports both sequential and parallel processing.

### Install

```bash
pip install pandas langdetect openpyxl
```

### Usage

**Standard batch detection** — edit the path and column in `detector.py`, then run:

```python
df_result = detect_languages_in_file(
    file_path="your_file.xlsx",
    text_column="content",
    batch_size=500
)
```

```bash
python detector.py
```

**Parallel detection** for large corpora (`LanBatch.py`):

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(detect_language, df[text_column]))
df["detected_lang"] = results
```

Adjust `max_workers` based on your CPU count.

### Output

| Column | Description |
|---|---|
| `detected_lang` | ISO 639-1 language code (e.g. `en`, `sv`, `de`) or `unknown` if detection fails |

Results are saved as `<original_filename>_with_lang.xlsx`.

> `DetectorFactory.seed = 0` ensures reproducible results. Empty or null entries return `unknown` without raising an error.

---

## Module 4 — Sentiment Analysis (VADER)

Multilingual sentiment analysis pipeline. Language is auto-detected; non-English text is translated to English via Google Translate before VADER scoring. Outputs a formatted XLSX with colour-coded sentiment labels.

### Install

```bash
pip install vaderSentiment langdetect deep-translator pandas openpyxl tqdm nltk
```

```python
import nltk
nltk.download('vader_lexicon')   # required for NLTK-based scripts
nltk.download('punkt')           # required for long_text.py
```

### Quick Examples

```bash
python core_use.py      # single text scoring
python monitor.py       # batch comment list
python long_text.py     # sentence-level analysis for long articles
```

### Full Corpus Pipeline

**1. Edit `config.py`:**

```python
INPUT_FILE  = "your_file.csv"      # path to your CSV or XLSX
TEXT_COLUMN = "content"             # column containing the text
OUTPUT_FILE = "vader_results.xlsx"
```

**2. Run:**

```bash
python main.py
```

Dependencies install automatically on first run.

### Sentiment Labels

| Label | Compound Score |
|---|---|
| Positive | ≥ 0.05 |
| Neutral | −0.05 to 0.05 |
| Negative | ≤ −0.05 |

### Output Columns

| Column | Description |
|---|---|
| `detected_lang` | Auto-detected language code (e.g. `en`, `zh-cn`, `fr`) |
| `text_for_vader` | Text fed to VADER (translated to English if needed) |
| `vader_neg / neu / pos` | Negative / Neutral / Positive ratio (0–1) |
| `vader_compound` | Overall sentiment score (−1 to +1) |
| `sentiment_label` | Positive / Neutral / Negative |

> The output `.xlsx` includes conditional colour-coding on `sentiment_label` (green / yellow / red) and a frozen header row.  
> For large corpora (1000+ rows), increase `TRANSLATE_DELAY` in `config.py` to avoid Google Translate rate limiting.

---

## Module 5 — Semantic Embedding

Sentence-level embedding, similarity calculation, and clustering using [Sentence Transformers](https://www.sbert.net/). Supports both quick comparisons and large-scale multilingual batch encoding.

### Install

```bash
pip install sentence-transformers scikit-learn pandas numpy openpyxl
```

### Scripts

| Script | Description |
|---|---|
| `BasicEmbedding.py` | Encode a list of sentences into dense vectors |
| `CalSim.py` | Compute cosine similarity between sentence pairs |
| `TextCluster.py` | Group texts into semantic clusters using K-Means |
| `MultLinModel.py` | Batch-encode a full `.xlsx` corpus; saves `embeddings.npy` |

### Usage

**Similarity check** (`CalSim.py`):

```bash
python CalSim.py
```

```
tensor([[0.8526]])   # high similarity
tensor([[0.0831]])   # low similarity
```

**Clustering** (`TextCluster.py`): replace `KirunaTextList` with your text list and adjust `n_clusters` as needed.

**Large-scale batch encoding** (`MultLinModel.py`): edit the file path and column, then run:

```bash
python MultLinModel.py
```

### Models Used

| Model | Use Case |
|---|---|
| `all-MiniLM-L6-v2` | Lightweight English model — fast similarity & clustering |
| `paraphrase-multilingual-MiniLM-L12-v2` | Multilingual — large corpus batch encoding |

---

## Requirements

- Python 3.7+

| Module | Key Dependencies |
|---|---|
| Post Cleaning | `pandas`, `openpyxl` |
| Reply Cleaning | `pandas`, `openpyxl` |
| Language Detection | `langdetect`, `pandas`, `openpyxl` |
| Sentiment Analysis | `vaderSentiment`, `langdetect`, `deep-translator`, `nltk`, `tqdm`, `pandas`, `openpyxl` |
| Semantic Embedding | `sentence-transformers`, `scikit-learn`, `numpy`, `pandas`, `openpyxl` |

Install all at once:

```bash
pip install pandas openpyxl langdetect vaderSentiment deep-translator nltk tqdm sentence-transformers scikit-learn numpy
```
