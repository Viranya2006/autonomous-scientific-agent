"""
Session Manager for Autonomous Scientific Agent

Manages research sessions with SQLite database for persistence,
tracking progress, status, and results.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages research sessions with database persistence"""

    def __init__(self, db_path: str = "data/sessions.db"):
        """Initialize session manager with database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    research_topic TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress INTEGER DEFAULT 0,
                    current_phase TEXT,
                    max_papers INTEGER,
                    max_hypotheses INTEGER,
                    iterations INTEGER,
                    ai_model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    results_path TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    phase TEXT,
                    message TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            conn.commit()

    def create_session(self, research_topic: str, max_papers: int = 20,
                       max_hypotheses: int = 10, iterations: int = 3,
                       ai_model: str = "gemini") -> str:
        """Create a new research session

        Args:
            research_topic: Research topic to investigate
            max_papers: Maximum papers to collect
            max_hypotheses: Maximum hypotheses to generate
            iterations: Number of research iterations
            ai_model: AI model to use (gemini/groq)

        Returns:
            session_id: Unique session identifier
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (session_id, research_topic, status, max_papers, max_hypotheses, 
                 iterations, ai_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, research_topic, "pending", max_papers,
                  max_hypotheses, iterations, ai_model))
            conn.commit()

        logger.info(
            f"Created session {session_id} for topic: {research_topic}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sessions, optionally filtered by status

        Args:
            status: Filter by status (pending/running/completed/failed)

        Returns:
            List of session dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if status:
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM sessions ORDER BY created_at DESC"
                )

            return [dict(row) for row in cursor.fetchall()]

    def update_session_status(self, session_id: str, status: str,
                              error_message: Optional[str] = None):
        """Update session status

        Args:
            session_id: Session identifier
            status: New status (pending/running/completed/failed)
            error_message: Optional error message for failed status
        """
        with sqlite3.connect(self.db_path) as conn:
            if status == "completed":
                conn.execute("""
                    UPDATE sessions 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP,
                        completed_at = CURRENT_TIMESTAMP, error_message = ?
                    WHERE session_id = ?
                """, (status, error_message, session_id))
            else:
                conn.execute("""
                    UPDATE sessions 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP,
                        error_message = ?
                    WHERE session_id = ?
                """, (status, error_message, session_id))
            conn.commit()

        logger.info(f"Session {session_id} status updated to: {status}")

    def update_session_progress(self, session_id: str, progress: int,
                                phase: str, message: Optional[str] = None):
        """Update session progress

        Args:
            session_id: Session identifier
            progress: Progress percentage (0-100)
            phase: Current phase name
            message: Optional progress message
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET progress = ?, current_phase = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (progress, phase, session_id))

            if message:
                conn.execute("""
                    INSERT INTO session_logs (session_id, phase, message)
                    VALUES (?, ?, ?)
                """, (session_id, phase, message))

            conn.commit()

        logger.debug(f"Session {session_id} progress: {progress}% - {phase}")

    def save_session_results(self, session_id: str, results_path: str):
        """Save path to session results

        Args:
            session_id: Session identifier
            results_path: Path to results directory
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET results_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (results_path, session_id))
            conn.commit()

    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get logs for a session

        Args:
            session_id: Session identifier

        Returns:
            List of log entries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM session_logs 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id: str):
        """Delete a session and its logs

        Args:
            session_id: Session identifier
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM session_logs WHERE session_id = ?", (session_id,))
            conn.execute(
                "DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()

        logger.info(f"Deleted session {session_id}")
