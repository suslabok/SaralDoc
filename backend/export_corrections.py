"""
Exports APPROVED clause corrections (see feedback_db.py, /feedback endpoints)
into datasets/corrections_dataset.csv, which trainer.py picks up
automatically alongside clause_dataset.csv and nepali_clause_dataset.csv.

Deliberately only exports corrections with status == 'approved' — pending
corrections need a human to look at them first (via GET /feedback/corrections
and POST /feedback/{id}/approve) so a careless or bad-faith correction can't
silently corrupt the training set. This is the real "grow the Nepali
dataset" path referenced in README.md Phase 2: actual user corrections on
actual uploaded documents, not more hand-authoring.

Usage:
    python export_corrections.py
    python trainer.py   # picks up the new corrections_dataset.csv automatically
"""
import csv
from pathlib import Path
from collections import Counter

from feedback_db import feedback_db

OUT_DIR = Path(__file__).parent / "datasets"
OUT_PATH = OUT_DIR / "corrections_dataset.csv"


def main():
    approved = feedback_db.list_corrections(status="approved")

    if not approved:
        print("No approved corrections yet.")
        print("Review pending ones first: GET /feedback/corrections?status=pending")
        print("Approve via: POST /feedback/{id}/approve")
        return

    rows = [
        (c["text"], c["corrected_type"], c["language"], "user_correction")
        for c in approved
    ]

    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label", "language", "source"])
        writer.writerows(rows)

    print(f"Wrote {len(rows)} approved corrections to {OUT_PATH}")
    print("By label:", dict(Counter(r[1] for r in rows)))
    print("By language:", dict(Counter(r[2] for r in rows)))
    print()
    print("Run `python trainer.py` to retrain with these included.")


if __name__ == "__main__":
    main()
