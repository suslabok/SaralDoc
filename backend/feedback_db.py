"""
Stores user corrections to clause-type predictions.

This is the Phase 2 answer to "we have no real Nepali data": every time a
user tells the app a clause was mis-classified, that correction is a real,
grounded training example — grown from actual documents people paste or
upload, unlike the hand-authored/translated seed corpus in
build_nepali_dataset.py. Corrections are stored here as PENDING and must be
reviewed (see export_corrections.py) before entering the training set, so
one bad-faith or mistaken correction can't silently poison the model.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager


class FeedbackDB:
    def __init__(self, db_file: str = "saraldoc.db"):
        # Shares the same SQLite file as history_db — one DB, multiple tables.
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clause_corrections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    text TEXT NOT NULL,
                    language TEXT NOT NULL,
                    predicted_type TEXT NOT NULL,
                    predicted_confidence REAL,
                    corrected_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    analysis_id INTEGER
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_corrections_status
                ON clause_corrections(status)
            """)

    def add_correction(
        self,
        text: str,
        language: str,
        predicted_type: str,
        corrected_type: str,
        predicted_confidence: Optional[float] = None,
        analysis_id: Optional[int] = None,
    ) -> Dict:
        timestamp = datetime.now().isoformat()
        with self._connect() as conn:
            cur = conn.execute("""
                INSERT INTO clause_corrections (
                    timestamp, text, language, predicted_type,
                    predicted_confidence, corrected_type, status, analysis_id
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                timestamp, text.strip(), language, predicted_type,
                predicted_confidence, corrected_type, analysis_id
            ))
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "timestamp": timestamp,
            "text": text.strip(),
            "language": language,
            "predicted_type": predicted_type,
            "corrected_type": corrected_type,
            "status": "pending",
        }

    def list_corrections(self, status: Optional[str] = None) -> List[Dict]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM clause_corrections WHERE status = ? ORDER BY timestamp DESC",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM clause_corrections ORDER BY timestamp DESC"
                ).fetchall()
        return [dict(row) for row in rows]

    def set_status(self, correction_id: int, status: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE clause_corrections SET status = ? WHERE id = ?",
                (status, correction_id),
            )
        return cur.rowcount > 0

    def stats(self) -> Dict:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT status, language, COUNT(*) AS count
                FROM clause_corrections GROUP BY status, language
            """).fetchall()
        out = {}
        for r in rows:
            out.setdefault(r["status"], {})[r["language"]] = r["count"]
        return out


feedback_db = FeedbackDB()
