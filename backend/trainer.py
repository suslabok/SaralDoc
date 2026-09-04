"""
Trains and evaluates a real clause-type classifier.

Previously this file was entirely disconnected from the app (no endpoint
called it) and its "evaluation" was hardcoded fake numbers
(`"extraction_confidence": 0.87` regardless of input). This version
actually trains a scikit-learn pipeline on datasets/clause_dataset.csv,
does a real stratified train/test split, reports real accuracy/F1 per
class, and saves the trained model so processor.py can load and use it.

Phase 1 (bilingual) update
---------------------------
Training data is now the UNION of two source files:
  - datasets/clause_dataset.csv         (CUAD-derived, English, real contracts)
  - datasets/nepali_clause_dataset.csv  (hand-authored Nepali seed clauses)
merged at train time (not on disk) so each source stays independently
reproducible/regeneratable. A `language` column has always existed in both
files; this version actually uses it to report accuracy PER LANGUAGE, since
a single blended accuracy number would hide a model that's great at English
and mediocre at Nepali (or vice versa) behind one average.

Usage:
    python generate_dataset.py       # (or build_real_dataset.py) builds the English CSV
    python build_nepali_dataset.py   # builds the Nepali CSV
    python trainer.py                # trains + evaluates + saves the model
"""
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import joblib

DATA_DIR = Path(__file__).parent / "datasets"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "clause_classifier.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

TOKEN_PATTERN = r"(?u)\b[\w\u0900-\u097F]+\b"

DEFAULT_DATASET_FILES = [
    "clause_dataset.csv",
    "nepali_clause_dataset.csv",
    "corrections_dataset.csv",  # approved user corrections; see export_corrections.py. Optional — fine if missing.
]


class ModelTrainer:
    """Trains the TF-IDF + Logistic Regression clause classifier"""

    def __init__(self, dataset_files=None):
        files = dataset_files if dataset_files is not None else DEFAULT_DATASET_FILES
        self.dataset_paths = [DATA_DIR / f for f in files]

    def load_dataset(self) -> Tuple[List[str], List[str], List[str]]:
        texts, labels, languages = [], [], []
        found_any = False
        for path in self.dataset_paths:
            if not path.exists():
                continue
            found_any = True
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    texts.append(row["text"])
                    labels.append(row["label"])
                    languages.append(row.get("language", "unknown"))
        if not found_any:
            raise FileNotFoundError(
                f"None of {[str(p) for p in self.dataset_paths]} exist. "
                f"Run `python generate_dataset.py` / `python build_real_dataset.py` "
                f"and `python build_nepali_dataset.py` first."
            )
        return texts, labels, languages

    def train(self, test_size: float = 0.2, random_state: int = 42) -> dict:
        texts, labels, languages = self.load_dataset()

        indices = list(range(len(texts)))
        idx_train, idx_test = train_test_split(
            indices,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )
        X_train = [texts[i] for i in idx_train]
        X_test = [texts[i] for i in idx_test]
        y_train = [labels[i] for i in idx_train]
        y_test = [labels[i] for i in idx_test]
        lang_test = [languages[i] for i in idx_test]

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                token_pattern=TOKEN_PATTERN,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=5.0,
                class_weight="balanced",
            )),
        ])

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        # Per-language accuracy: a single blended number hides whether the
        # model actually works for Nepali or is just riding on the much
        # larger English/CUAD portion of the training set.
        per_language = defaultdict(lambda: {"correct": 0, "total": 0})
        for true, pred, lang in zip(y_test, y_pred, lang_test):
            per_language[lang]["total"] += 1
            if true == pred:
                per_language[lang]["correct"] += 1
        per_language_accuracy = {
            lang: {
                "accuracy": round(v["correct"] / v["total"], 4) if v["total"] else 0.0,
                "test_samples": v["total"],
            }
            for lang, v in per_language.items()
        }

        train_lang_counts = defaultdict(int)
        for i in idx_train:
            train_lang_counts[languages[i]] += 1

        MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)

        metadata = {
            "model_type": "TF-IDF + Logistic Regression",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "total_samples": len(texts),
            "training_samples_by_language": dict(train_lang_counts),
            "classes": sorted(set(labels)),
            "accuracy": round(accuracy, 4),
            "accuracy_by_language": per_language_accuracy,
            "per_class_f1": {
                label: round(report[label]["f1-score"], 4)
                for label in sorted(set(labels)) if label in report
            },
            "macro_avg_f1": round(report["macro avg"]["f1-score"], 4),
            "weighted_avg_f1": round(report["weighted avg"]["f1-score"], 4),
        }
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return {"metadata": metadata, "full_report": report}


def main():
    trainer = ModelTrainer()
    result = trainer.train()
    meta = result["metadata"]

    print(f"Trained on {meta['training_samples']} samples, tested on {meta['test_samples']}")
    print(f"Training samples by language: {meta['training_samples_by_language']}")
    print(f"Overall accuracy: {meta['accuracy']:.1%}")
    print()
    print("Accuracy by language (this is the number that matters for Nepali):")
    for lang, stats in meta["accuracy_by_language"].items():
        print(f"  {lang:10s} {stats['accuracy']:.1%}  (n={stats['test_samples']})")
    print()
    print(f"Macro-avg F1:     {meta['macro_avg_f1']:.4f}")
    print()
    print("Per-class F1:")
    for label, f1 in meta["per_class_f1"].items():
        print(f"  {label:16s} {f1:.4f}")
    print()
    print(f"Model saved to {MODEL_PATH}")
    print(f"Metadata saved to {METADATA_PATH}")


if __name__ == "__main__":
    main()
