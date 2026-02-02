"""
Persistent memory using SQLite for conversation tracking.
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import Config


class PersistentMemory:
    """SQLite-based memory for session persistence."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.MEMORY_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Search history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User interactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                intent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job applications (for tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                job_url TEXT,
                status TEXT DEFAULT 'DRAFT',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def save_search(self, query: str, results_count: int):
        """Save a search query."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO searches (query, results_count) VALUES (?, ?)",
            (query, results_count)
        )
        self.conn.commit()
    
    def get_recent_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search queries."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT query, results_count, timestamp FROM searches ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {"query": row[0], "results_count": row[1], "timestamp": row[2]}
            for row in rows
        ]
    
    def save_interaction(self, user_input: str, agent_response: str, intent: Optional[str] = None):
        """Save a user-agent interaction."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (user_input, agent_response, intent) VALUES (?, ?, ?)",
            (user_input, agent_response[:500], intent)  # Limit response size
        )
        self.conn.commit()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_input, agent_response, intent, timestamp FROM interactions ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return [
            {
                "user_input": row[0],
                "agent_response": row[1],
                "intent": row[2],
                "timestamp": row[3]
            }
            for row in rows
        ]
    
    def save_application(self, job_title: str, company: str, job_url: str, status: str = "DRAFT"):
        """Track a job application."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO applications (job_title, company, job_url, status) VALUES (?, ?, ?, ?)",
            (job_title, company, job_url, status)
        )
        self.conn.commit()
    
    def get_applications(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get job applications, optionally filtered by status."""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT job_title, company, job_url, status, timestamp FROM applications WHERE status = ? ORDER BY timestamp DESC",
                (status,)
            )
        else:
            cursor.execute(
                "SELECT job_title, company, job_url, status, timestamp FROM applications ORDER BY timestamp DESC"
            )
        rows = cursor.fetchall()
        return [
            {
                "job_title": row[0],
                "company": row[1],
                "job_url": row[2],
                "status": row[3],
                "timestamp": row[4]
            }
            for row in rows
        ]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
