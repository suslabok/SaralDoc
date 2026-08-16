"""
Builds datasets/clause_dataset.csv from REAL labeled contract data (CUAD —
Contract Understanding Atticus Dataset), replacing the previous
template-generated synthetic dataset.

CUAD v1: 510 real commercial contracts, 13,000+ expert annotations across
41 clause categories, curated by The Atticus Project (CC BY 4.0 license).
Source: https://github.com/TheAtticusProject/cuad

IMPORTANT — taxonomy change: CUAD's categories are built for M&A due
diligence, not everyday contract reading. Of the 9 original clause types,
only `governing_law`, `termination`, and `penalty` have a clean real-data
equivalent in CUAD. This script REPLACES the old 9-class taxonomy with an
8-class taxonomy built entirely from real, well-populated CUAD categories:

    governing_law   <- "Governing Law"              (real, direct match)
    termination     <- "Termination For Convenience" (real, narrower scope)
    penalty         <- "Liquidated Damages"          (real, proxy)
    license_grant   <- "License Grant"               (new)
    liability_cap   <- "Cap On Liability"             (new, replaces "indemnity")
    insurance       <- "Insurance"                    (new)
    non_compete     <- "Non-Compete"                  (new)
    audit_rights    <- "Audit Rights"                 (new)
    general         <- sampled non-clause contract text (negative class)

Dropped (no real English equivalent found in CUAD): payment, obligation,
confidentiality, definition. Nepali is NOT included here - no public
labeled Nepali legal-clause corpus exists; that requires real documents
supplied separately (see ROADMAP.md).

Usage:
    python build_real_dataset.py
    (expects datasets/raw/cuad_data.zip - CUAD's data.zip from
     https://github.com/TheAtticusProject/cuad/raw/main/data.zip;
     downloads it automatically if missing and internet is available)
"""
import csv
import json
import random
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

random.seed(42)

RAW_DIR = Path(__file__).parent / "datasets" / "raw"
OUT_DIR = Path(__file__).parent / "datasets"
ZIP_PATH = RAW_DIR / "cuad_data.zip"
JSON_PATH = RAW_DIR / "CUADv1.json"
CUAD_ZIP_URL = "https://github.com/TheAtticusProject/cuad/raw/main/data.zip"

CATEGORY_MAP = {
    "Governing Law": "governing_law",
    "Termination For Convenience": "termination",
    "Liquidated Damages": "penalty",
    "License Grant": "license_grant",
    "Cap On Liability": "liability_cap",
    "Insurance": "insurance",
    "Non-Compete": "non_compete",
    "Audit Rights": "audit_rights",
}

# Cap how many examples we take per category so a few huge categories
# (License Grant: 777, Audit Rights: 643) don't swamp the smaller ones
# (Liquidated Damages: 121). Keeps classes reasonably balanced.
MAX_PER_CATEGORY = 150
GENERAL_TARGET = 130
MIN_WORDS = 6
MAX_WORDS = 120

# EDGAR/SEC filing noise patterns to reject: page footers, redacted
# confidential terms (e.g. "[ * ]", "[***]"), and other filing boilerplate
# that isn't actually clause prose.
JUNK_PATTERNS = [
    re.compile(r"\[\s?\*+\s?\]"),          # [*], [ * ], [***] redactions
    re.compile(r"^-?\s?\d+\s?-\s?Source:", re.IGNORECASE),  # "-69- Source: ..."
    re.compile(r"\bSource:\s*[A-Z][A-Z0-9 ,.\-]+\d{1,2}/\d{1,2}/\d{2,4}"),  # filing citation
    re.compile(r"^\s*-?\s?\d+\s?-\s*$"),   # bare page numbers like "- 69 -"
]


def is_junk(text: str) -> bool:
    return any(p.search(text) for p in JUNK_PATTERNS)


def ensure_raw_data():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if JSON_PATH.exists():
        return
    if not ZIP_PATH.exists():
        print(f"Downloading CUAD data.zip from {CUAD_ZIP_URL} ...")
        urllib.request.urlretrieve(CUAD_ZIP_URL, ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extract("CUADv1.json", RAW_DIR)


def category_of(qa_id: str) -> str:
    return qa_id.split("__")[-1]


def collect_positive_examples():
    """Extract real clause text spans for our 8 mapped categories."""
    with open(JSON_PATH, encoding="utf-8") as f:
        cuad = json.load(f)

    by_category = defaultdict(list)
    seen_texts = set()

    for contract in cuad["data"]:
        for para in contract["paragraphs"]:
            for qa in para["qas"]:
                raw_cat = category_of(qa["id"])
                label = CATEGORY_MAP.get(raw_cat)
                if not label or qa["is_impossible"]:
                    continue
                for ans in qa["answers"]:
                    text = re.sub(r"\s+", " ", ans["text"]).strip()
                    word_count = len(text.split())
                    if word_count < MIN_WORDS or word_count > MAX_WORDS:
                        continue
                    if text in seen_texts:
                        continue
                    if is_junk(text):
                        continue
                    seen_texts.add(text)
                    by_category[label].append(text)

    rows = []
    for label, texts in by_category.items():
        random.shuffle(texts)
        for text in texts[:MAX_PER_CATEGORY]:
            rows.append((text, label, "english"))
    return rows, seen_texts


def collect_negative_examples(exclude_texts):
    """Sample real contract sentences that are NOT any labeled clause span,
    to serve as the 'general' negative class."""
    with open(JSON_PATH, encoding="utf-8") as f:
        cuad = json.load(f)

    candidates = []
    sentence_split = re.compile(r"(?<=[.!?])\s+")

    for contract in cuad["data"][:120]:  # sample from a subset of contracts for speed
        for para in contract["paragraphs"]:
            context = para["context"]
            for sentence in sentence_split.split(context):
                sentence = re.sub(r"\s+", " ", sentence).strip()
                word_count = len(sentence.split())
                if word_count < MIN_WORDS or word_count > MAX_WORDS:
                    continue
                if sentence in exclude_texts:
                    continue
                if is_junk(sentence):
                    continue
                # crude filter: skip if it looks like it belongs to one of
                # our positive categories (contains obvious trigger words)
                lowered = sentence.lower()
                if any(kw in lowered for kw in [
                    "governing law", "governed by the laws",
                    "terminate this agreement for convenience",
                    "liquidated damages", "license is granted", "grants a license",
                    "cap on liability", "limitation of liability",
                    "maintain insurance", "shall not compete", "audit the books",
                ]):
                    continue
                candidates.append(sentence)

    random.shuffle(candidates)
    unique = list(dict.fromkeys(candidates))  # dedupe, preserve order
    return [(text, "general", "english") for text in unique[:GENERAL_TARGET]]


def main():
    ensure_raw_data()
    positive_rows, seen_texts = collect_positive_examples()
    negative_rows = collect_negative_examples(seen_texts)

    all_rows = positive_rows + negative_rows
    random.shuffle(all_rows)

    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / "clause_dataset.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "language"])
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} REAL labeled examples to {out_path}")
    print("Source: CUAD v1 (The Atticus Project, CC BY 4.0)")
    print("Label distribution:", dict(Counter(r[1] for r in all_rows)))


if __name__ == "__main__":
    main()