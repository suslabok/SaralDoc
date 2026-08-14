"""
Trains and evaluates a real clause-type classifier.

Previously this file was entirely disconnected from the app (no endpoint
called it) and its "evaluation" was hardcoded fake numbers
(`"extraction_confidence": 0.87` regardless of input). This version
actually trains a scikit-learn pipeline on datasets/clause_dataset.csv,
does a real stratified train/test split, reports real accuracy/F1 per
class, and saves the trained model so processor.py can load and use it.

Usage:
    python generate_dataset.py     # builds datasets/clause_dataset.csv (once)
    python trainer.py              # trains + evaluates + saves the model
"""
import csv
import json
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


class ModelTrainer:
    """Trains the TF-IDF + Logistic Regression clause classifier"""

    def __init__(self, dataset_file: str = "clause_dataset.csv"):
        self.dataset_path = DATA_DIR / dataset_file

    def load_dataset(self) -> Tuple[List[str], List[str]]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}. "
                f"Run `python generate_dataset.py` first."
            )
        texts, labels = [], []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row["text"])
                labels.append(row["label"])
        return texts, labels

    def train(self, test_size: float = 0.2, random_state: int = 42) -> dict:
        texts, labels = self.load_dataset()

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels,
        )

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

        MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(pipeline, MODEL_PATH)

        metadata = {
            "model_type": "TF-IDF + Logistic Regression",
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "total_samples": len(texts),
            "classes": sorted(set(labels)),
            "accuracy": round(accuracy, 4),
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
    print(f"Overall accuracy: {meta['accuracy']:.1%}")
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
