"""
History storage for SaralDoc analyses.
SQLite-backed (was a flat JSON file) — same public API as before, so
main.py and everything else that imports `history_db` needs no changes.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager


class HistoryDB:
    """SQLite-based history database for storing document analyses"""

    def __init__(self, db_file: str = "saraldoc.db"):
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
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    clauses_count INTEGER NOT NULL DEFAULT 0,
                    obligations_count INTEGER NOT NULL DEFAULT 0,
                    entities_count INTEGER NOT NULL DEFAULT 0,
                    complexity_score INTEGER NOT NULL DEFAULT 0,
                    readability_score INTEGER NOT NULL DEFAULT 0,
                    full_analysis TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_timestamp
                ON analyses(timestamp DESC)
            """)

    def add_analysis(self, analysis: Dict) -> Dict:
        """Add new analysis to history"""
        timestamp = datetime.now().isoformat()
        document_name = analysis.get('document_name', 'Untitled')
        language = analysis.get('language', 'unknown')
        clauses_count = len(analysis.get('clauses', []))
        obligations_count = len(analysis.get('obligations', []))
        entities_count = len(analysis.get('entities', []))
        complexity_score = analysis.get('complexity_score', 0)
        readability_score = analysis.get('readability_score', 0)
        full_analysis = json.dumps(analysis, ensure_ascii=False)

        with self._connect() as conn:
            cur = conn.execute("""
                INSERT INTO analyses (
                    timestamp, document_name, language, clauses_count,
                    obligations_count, entities_count, complexity_score,
                    readability_score, full_analysis
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, document_name, language, clauses_count,
                obligations_count, entities_count, complexity_score,
                readability_score, full_analysis
            ))
            new_id = cur.lastrowid

        return {
            'id': new_id,
            'timestamp': timestamp,
            'document_name': document_name,
            'language': language,
            'clauses_count': clauses_count,
            'obligations_count': obligations_count,
            'entities_count': entities_count,
            'complexity_score': complexity_score,
            'readability_score': readability_score,
            'full_analysis': analysis
        }

    def get_all_history(self) -> List[Dict]:
        """Get all analyses (without full analysis payload for performance)"""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT id, timestamp, document_name, language, clauses_count,
                       obligations_count, entities_count, complexity_score,
                       readability_score
                FROM analyses
                ORDER BY timestamp DESC
            """).fetchall()
        return [dict(row) for row in rows]

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """Get full analysis by ID"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT full_analysis FROM analyses WHERE id = ?",
                (analysis_id,)
            ).fetchone()
        if row is None:
            return None
        return json.loads(row['full_analysis'])

    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete analysis by ID"""
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        return cur.rowcount > 0

    def clear_history(self) -> bool:
        """Clear all history"""
        with self._connect() as conn:
            conn.execute("DELETE FROM analyses")
        return True

    def get_stats(self) -> Dict:
        """Get statistics about analyses"""
        with self._connect() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) AS total_analyses,
                    COALESCE(SUM(clauses_count), 0) AS total_clauses,
                    COALESCE(SUM(obligations_count), 0) AS total_obligations,
                    COALESCE(AVG(complexity_score), 0) AS average_complexity
                FROM analyses
            """).fetchone()

            lang_rows = conn.execute("""
                SELECT language, COUNT(*) AS count
                FROM analyses
                GROUP BY language
            """).fetchall()

        if row['total_analyses'] == 0:
            return {
                'total_analyses': 0,
                'total_clauses': 0,
                'total_obligations': 0,
                'average_complexity': 0,
                'languages': {}
            }

        return {
            'total_analyses': row['total_analyses'],
            'total_clauses': row['total_clauses'],
            'total_obligations': row['total_obligations'],
            'average_complexity': round(row['average_complexity'], 2),
            'languages': {r['language']: r['count'] for r in lang_rows}
        }


# Global instance
history_db = HistoryDB()
