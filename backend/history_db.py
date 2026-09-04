"""
History storage for SaralDoc analyses.
SQLite-backed. Same public API as before EXCEPT every method now takes a
`user_id` (Google account `sub`) and every query is scoped to it.

Why this changed
------------------
Every /history endpoint in main.py used to read/delete from this table with
no ownership check at all: any client — signed in or not, whichever account
— could list, read, or bulk-delete every analysis ever run by anyone. That
was a real privacy/data-integrity bug, not a theoretical one, given
document text and full clause breakdowns are stored in `full_analysis`.

Rows created before this change have user_id = NULL ("legacy" rows). They
are intentionally excluded from all scoped queries below (nobody's session
matches NULL) rather than migrated to a guess — there was no reliable way
to know who they belonged to.
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
        print(f"[history_db] schema ready (user_id-scoped, migration-safe build) - {self.db_file}")

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
            # Migration: DBs created before user_id existed won't have the
            # column. This MUST run before anything below that touches
            # user_id (indexes, queries) - indexing/querying a column that
            # doesn't exist yet on a pre-existing DB file throws
            # "no such column: user_id".
            existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(analyses)")}
            if "user_id" not in existing_cols:
                conn.execute("ALTER TABLE analyses ADD COLUMN user_id TEXT")
                existing_cols.add("user_id")

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_analyses_timestamp
                ON analyses(timestamp DESC)
            """)
            # Defensive: only touch the user_id index if the column is
            # actually confirmed present. This can never fire in normal
            # operation (the migration above guarantees it), but if it
            # somehow does (e.g. a stale copy of this file elsewhere on
            # disk, a half-applied update), skip the index instead of
            # crashing the whole app on startup.
            if "user_id" in existing_cols:
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_analyses_user
                    ON analyses(user_id)
                """)
            else:
                print(
                    "[history_db] WARNING: user_id column still missing after "
                    "migration attempt - skipping index. This should not happen; "
                    "check for a stale/duplicate history_db.py on disk."
                )

    def add_analysis(self, analysis: Dict, user_id: Optional[str]) -> Dict:
        """Add new analysis to history, owned by user_id (None for
        anonymous/unauthenticated requests — see main.py, these are not
        persisted to a queryable history at all, only returned in the
        response, to avoid an ever-growing table nobody can retrieve)."""
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
                    readability_score, full_analysis, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, document_name, language, clauses_count,
                obligations_count, entities_count, complexity_score,
                readability_score, full_analysis, user_id
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

    def get_all_history(self, user_id: str) -> List[Dict]:
        """Get all analyses belonging to user_id (without the full analysis
        payload, for list-view performance)."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT id, timestamp, document_name, language, clauses_count,
                       obligations_count, entities_count, complexity_score,
                       readability_score
                FROM analyses
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,)).fetchall()
        return [dict(row) for row in rows]

    def get_analysis_by_id(self, analysis_id: int, user_id: str) -> Optional[Dict]:
        """Get full analysis by ID, only if it belongs to user_id."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT full_analysis FROM analyses WHERE id = ? AND user_id = ?",
                (analysis_id, user_id)
            ).fetchone()
        if row is None:
            return None
        return json.loads(row['full_analysis'])

    def delete_analysis(self, analysis_id: int, user_id: str) -> bool:
        """Delete analysis by ID, only if it belongs to user_id."""
        with self._connect() as conn:
            cur = conn.execute(
                "DELETE FROM analyses WHERE id = ? AND user_id = ?",
                (analysis_id, user_id)
            )
        return cur.rowcount > 0

    def clear_history(self, user_id: str) -> bool:
        """Clear history belonging to user_id only."""
        with self._connect() as conn:
            conn.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
        return True

    def get_stats(self, user_id: str) -> Dict:
        """Get statistics about user_id's analyses only."""
        with self._connect() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) AS total_analyses,
                    COALESCE(SUM(clauses_count), 0) AS total_clauses,
                    COALESCE(SUM(obligations_count), 0) AS total_obligations,
                    COALESCE(AVG(complexity_score), 0) AS average_complexity
                FROM analyses
                WHERE user_id = ?
            """, (user_id,)).fetchone()

            lang_rows = conn.execute("""
                SELECT language, COUNT(*) AS count
                FROM analyses
                WHERE user_id = ?
                GROUP BY language
            """, (user_id,)).fetchall()

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