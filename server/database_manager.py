"""
Database Manager Module

Handles all SQLite database operations for the Q&A application.
"""

import logging

# import asyncio  # Unused for now
# import aiosqlite  # Unused for now
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for users and events."""

    def __init__(self, db_path: str = "data/qa_database.db"):
        """
        Initialize the DatabaseManager.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")

    def initialize_database(self):
        """Initialize the database with required tables and indexes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create users table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        first_seen TIMESTAMP NOT NULL,
                        last_seen TIMESTAMP NOT NULL,
                        total_questions INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create events table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username TEXT NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        ip_address TEXT,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """
                )

                # Create indexes for performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_username ON events (username)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_date ON events (DATE(timestamp))"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_events_user_id ON events (user_id)"
                )

                conn.commit()
                logger.info("✅ Database initialized successfully")

        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")
            raise

    def get_or_create_user(
        self, username: str, ip_address: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing user or create new one.

        Args:
            username (str): Username to find or create
            ip_address (str, optional): IP address for logging

        Returns:
            Dict[str, Any]: User record
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Try to get existing user
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()

                now = datetime.now(timezone.utc).isoformat()

                if user:
                    # Update last_seen
                    cursor.execute(
                        """
                        UPDATE users
                        SET last_seen = ?, updated_at = ?
                        WHERE username = ?
                    """,
                        (now, now, username),
                    )

                    # Get updated user
                    cursor.execute(
                        "SELECT * FROM users WHERE username = ?", (username,)
                    )
                    user = cursor.fetchone()
                else:
                    # Create new user
                    cursor.execute(
                        """
                        INSERT INTO users (username, first_seen, last_seen, total_questions, created_at, updated_at)
                        VALUES (?, ?, ?, 0, ?, ?)
                    """,
                        (username, now, now, now, now),
                    )

                    user_id = cursor.lastrowid
                    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                    user = cursor.fetchone()

                    logger.info(f"👤 New user created: {username}")

                conn.commit()
                return dict(user) if user else None

        except Exception as e:
            logger.error(f"❌ Error managing user {username}: {e}")
            raise

    def log_event(
        self,
        username: str,
        question: str,
        answer: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> int:
        """
        Log a Q&A event to the database.

        Args:
            username (str): Username who asked the question
            question (str): The question asked
            answer (str): The answer provided
            ip_address (str, optional): User's IP address
            session_id (str, optional): Session identifier
            timestamp (str, optional): Custom timestamp (ISO format)

        Returns:
            int: Event ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get user info
                user = self.get_or_create_user(username, ip_address)
                user_id = user["id"] if user else None

                # Use provided timestamp or current time
                if not timestamp:
                    timestamp = datetime.now(timezone.utc).isoformat()

                # Insert event
                cursor.execute(
                    """
                    INSERT INTO events (user_id, username, question, answer, timestamp, ip_address, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        username,
                        question,
                        answer,
                        timestamp,
                        ip_address,
                        session_id,
                    ),
                )

                event_id = cursor.lastrowid

                # Update user's total questions count
                cursor.execute(
                    """
                    UPDATE users
                    SET total_questions = total_questions + 1,
                        updated_at = ?
                    WHERE id = ?
                """,
                    (datetime.now(timezone.utc).isoformat(), user_id),
                )

                conn.commit()
                logger.info(f"📝 Event logged: {username} -> Event ID {event_id}")
                return event_id

        except Exception as e:
            logger.error(f"❌ Error logging event for {username}: {e}")
            raise

    def get_user_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()

                if user:
                    return dict(user)
                return None

        except Exception as e:
            logger.error(f"❌ Error getting stats for user {username}: {e}")
            return None

    def get_daily_events(self, date: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all events for a specific date.

        Args:
            date (str): Date in YYYY-MM-DD format
            limit (int): Maximum number of events to return

        Returns:
            List[Dict[str, Any]]: List of event records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM events
                    WHERE DATE(timestamp) = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """,
                    (date, limit),
                )

                events = cursor.fetchall()
                return [dict(event) for event in events]

        except Exception as e:
            logger.error(f"❌ Error getting events for date {date}: {e}")
            return []

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM users ORDER BY total_questions DESC")
                users = cursor.fetchall()
                return [dict(user) for user in users]

        except Exception as e:
            logger.error(f"❌ Error getting all users: {e}")
            return []

    def get_analytics(self) -> Dict[str, Any]:
        """Get basic analytics from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Total users
                cursor.execute("SELECT COUNT(*) as total_users FROM users")
                total_users = cursor.fetchone()["total_users"]

                # Total events
                cursor.execute("SELECT COUNT(*) as total_events FROM events")
                total_events = cursor.fetchone()["total_events"]

                # Events per day (last 7 days)
                cursor.execute(
                    """
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM events
                    WHERE timestamp >= datetime('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """
                )
                daily_events = [dict(row) for row in cursor.fetchall()]

                # Top users
                cursor.execute(
                    """
                    SELECT username, total_questions
                    FROM users
                    ORDER BY total_questions DESC
                    LIMIT 10
                """
                )
                top_users = [dict(row) for row in cursor.fetchall()]

                return {
                    "total_users": total_users,
                    "total_events": total_events,
                    "daily_events": daily_events,
                    "top_users": top_users,
                }

        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return {}

    def close(self):
        """Close database connections."""
        # SQLite connections are closed automatically with context manager
        pass


if __name__ == "__main__":
    # Test the database manager
    logging.basicConfig(level=logging.INFO)

    db = DatabaseManager()
    db.initialize_database()

    print("Testing DatabaseManager...")

    # Test user creation
    user = db.get_or_create_user("test_user", "127.0.0.1")
    print(f"Created user: {user}")

    # Test event logging
    event_id = db.log_event(
        "test_user", "What is 2+2?", "Four!", "127.0.0.1", "sess_123"
    )
    print(f"Logged event ID: {event_id}")

    # Test analytics
    analytics = db.get_analytics()
    print(f"Analytics: {analytics}")
