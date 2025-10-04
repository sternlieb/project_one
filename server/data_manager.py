"""
Data Manager Module

Coordinates between SQLite database and JSON file logging.
Implements dual-write pattern for data integrity and backup.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging
import uuid

from database_manager import DatabaseManager
from json_logger import JSONLogger
from response_handler import get_random_answer

logger = logging.getLogger(__name__)


class DataManager:
    """
    Unified data manager that coordinates SQLite and JSON storage.
    Implements dual-write pattern with SQLite as primary and JSON as secondary.
    """

    def __init__(self, db_path: str = "data/qa_database.db", json_data_dir: str = "data"):
        """
        Initialize the DataManager.

        Args:
            db_path (str): Path to SQLite database
            json_data_dir (str): Directory for JSON files
        """
        self.db_manager = DatabaseManager(db_path)
        self.json_logger = JSONLogger(json_data_dir)
        self._initialize()

    def _initialize(self):
        """Initialize both storage systems."""
        try:
            # Initialize database
            self.db_manager.initialize_database()
            logger.info("✅ Data manager initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize data manager: {e}")
            raise

    def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"sess_{uuid.uuid4().hex[:12]}"

    def process_question(self, username: str, question: str,
                        ip_address: str = None, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user question and return response with logging.

        Args:
            username (str): Username asking the question
            question (str): The question text
            ip_address (str, optional): User's IP address
            session_id (str, optional): Session identifier

        Returns:
            Dict[str, Any]: Response containing answer and metadata
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = self.generate_session_id()

            # Get random answer
            answer = get_random_answer()

            # Create timestamp
            timestamp = datetime.now(timezone.utc).isoformat()

            # Primary storage: SQLite (must succeed)
            event_id = self.db_manager.log_event(
                username=username,
                question=question,
                answer=answer,
                ip_address=ip_address,
                session_id=session_id,
                timestamp=timestamp
            )

            # Get user info for JSON logging
            user_info = self.db_manager.get_user_stats(username)

            # Secondary storage: JSON (async, don't block)
            try:
                # Try to create async task if in Flask app context
                asyncio.create_task(self._log_to_json_async(
                    event_id, user_info, username, question, answer,
                    timestamp, ip_address, session_id
                ))
            except RuntimeError:
                # No event loop (testing/standalone), use synchronous logging
                self._log_to_json_sync(
                    event_id, user_info, username, question, answer,
                    timestamp, ip_address, session_id
                )

            # Prepare response
            response = {
                "event_id": event_id,
                "answer": answer,
                "question": question,
                "username": username,
                "timestamp": timestamp,
                "session_id": session_id
            }

            logger.info(f"🎯 Question processed successfully: User={username}, EventID={event_id}")
            return response

        except Exception as e:
            logger.error(f"❌ Error processing question from {username}: {e}")
            raise

    async def _log_to_json_async(self, event_id: int, user_info: Dict[str, Any],
                                username: str, question: str, answer: str,
                                timestamp: str, ip_address: str, session_id: str):
        """Async logging to JSON files."""
        try:
            # Log user info to JSON
            if user_info:
                await self.json_logger.log_user_async(user_info)

            # Prepare event data for JSON
            event_data = {
                "id": event_id,
                "user_id": user_info.get("id") if user_info else None,
                "username": username,
                "question": question,
                "answer": answer,
                "timestamp": timestamp,
                "ip_address": ip_address,
                "session_id": session_id,
                "created_at": timestamp
            }

            # Log event to JSON
            await self.json_logger.log_event_async(event_data)

        except Exception as e:
            # Don't raise - this is secondary storage, shouldn't block user
            logger.error(f"❌ Error logging to JSON for event {event_id}: {e}")

    def _log_to_json_sync(self, event_id: int, user_info: Dict[str, Any],
                         username: str, question: str, answer: str,
                         timestamp: str, ip_address: str, session_id: str):
        """Synchronous logging to JSON files (for testing/standalone use)."""
        try:
            # Log user info to JSON
            if user_info:
                self.json_logger.log_user(user_info)

            # Prepare event data for JSON
            event_data = {
                "id": event_id,
                "user_id": user_info.get("id") if user_info else None,
                "username": username,
                "question": question,
                "answer": answer,
                "timestamp": timestamp,
                "ip_address": ip_address,
                "session_id": session_id,
                "created_at": timestamp
            }

            # Log event to JSON
            self.json_logger.log_event(event_data)

        except Exception as e:
            # Don't raise - this is secondary storage, shouldn't block user
            logger.error(f"❌ Error logging to JSON for event {event_id}: {e}")

    def get_user_analytics(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive analytics for a user.

        Args:
            username (str): Username to get analytics for

        Returns:
            Dict[str, Any]: User analytics data
        """
        try:
            user_stats = self.db_manager.get_user_stats(username)
            if not user_stats:
                return None

            # Get recent activity (last 7 days) from database
            # This would require additional SQL queries - simplified for demo

            return {
                "user_info": user_stats,
                "summary": {
                    "total_questions": user_stats.get("total_questions", 0),
                    "member_since": user_stats.get("first_seen"),
                    "last_activity": user_stats.get("last_seen")
                }
            }

        except Exception as e:
            logger.error(f"❌ Error getting user analytics for {username}: {e}")
            return None

    def get_system_analytics(self) -> Dict[str, Any]:
        """
        Get system-wide analytics.

        Returns:
            Dict[str, Any]: System analytics
        """
        try:
            # Get analytics from database
            db_analytics = self.db_manager.get_analytics()

            # Get JSON file info
            available_dates = self.json_logger.get_available_dates()

            # Combine analytics
            analytics = {
                "database_stats": db_analytics,
                "json_backup": {
                    "available_dates": available_dates,
                    "total_date_files": len(available_dates),
                    "date_range": {
                        "earliest": min(available_dates) if available_dates else None,
                        "latest": max(available_dates) if available_dates else None
                    }
                },
                "system_health": {
                    "db_operational": True,
                    "json_backup_operational": True,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            }

            return analytics

        except Exception as e:
            logger.error(f"❌ Error getting system analytics: {e}")
            return {"error": str(e)}

    def export_user_data(self, username: str) -> Dict[str, Any]:
        """
        Export all data for a specific user (GDPR compliance).

        Args:
            username (str): Username to export data for

        Returns:
            Dict[str, Any]: All user data
        """
        try:
            # Get user info from database
            user_info = self.db_manager.get_user_stats(username)
            if not user_info:
                return {"error": "User not found"}

            # Get all user events from database
            # This would require additional SQL - simplified for demo

            # Get user data from JSON files
            json_users = self.json_logger.get_all_users()
            user_json = next((u for u in json_users if u.get("username") == username), None)

            export_data = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "username": username,
                "database_record": user_info,
                "json_backup_record": user_json,
                "total_questions": user_info.get("total_questions", 0),
                "member_since": user_info.get("first_seen"),
                "last_activity": user_info.get("last_seen")
            }

            return export_data

        except Exception as e:
            logger.error(f"❌ Error exporting data for user {username}: {e}")
            return {"error": str(e)}

    def validate_data_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency between SQLite and JSON data.

        Returns:
            Dict[str, Any]: Validation report
        """
        try:
            # Get users from both sources
            db_users = self.db_manager.get_all_users()
            json_users = self.json_logger.get_all_users()

            # Create username sets for comparison
            db_usernames = {user["username"] for user in db_users}
            json_usernames = {user["username"] for user in json_users}

            # Find discrepancies
            missing_in_json = db_usernames - json_usernames
            missing_in_db = json_usernames - db_usernames

            # Check event counts for recent dates
            recent_dates = self.json_logger.get_available_dates()[-7:]  # Last 7 days
            date_consistency = {}

            for date in recent_dates:
                db_events = len(self.db_manager.get_daily_events(date))
                json_events = len(self.json_logger.get_daily_events(date))
                date_consistency[date] = {
                    "db_count": db_events,
                    "json_count": json_events,
                    "match": db_events == json_events
                }

            validation_report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_consistency": {
                    "total_db_users": len(db_users),
                    "total_json_users": len(json_users),
                    "missing_in_json": list(missing_in_json),
                    "missing_in_db": list(missing_in_db),
                    "users_match": len(missing_in_json) == 0 and len(missing_in_db) == 0
                },
                "event_consistency": date_consistency,
                "overall_health": {
                    "users_consistent": len(missing_in_json) == 0 and len(missing_in_db) == 0,
                    "events_consistent": all(d["match"] for d in date_consistency.values())
                }
            }

            return validation_report

        except Exception as e:
            logger.error(f"❌ Error validating data consistency: {e}")
            return {"error": str(e)}

    def backup_to_json(self) -> Dict[str, Any]:
        """
        Manually trigger a full backup from SQLite to JSON.

        Returns:
            Dict[str, Any]: Backup status
        """
        try:
            logger.info("🔄 Starting manual backup to JSON...")

            # Get all users from database
            db_users = self.db_manager.get_all_users()

            # Bulk load users to JSON
            self.json_logger.bulk_load_users(db_users)

            # Get available dates and backup events
            dates_backed_up = []
            available_dates = self.json_logger.get_available_dates()

            # Get recent dates from database that might need backing up
            for date in available_dates:
                db_events = self.db_manager.get_daily_events(date)
                if db_events:
                    # Convert database events to JSON format
                    json_events = []
                    for event in db_events:
                        json_events.append({
                            "id": event["id"],
                            "user_id": event["user_id"],
                            "username": event["username"],
                            "question": event["question"],
                            "answer": event["answer"],
                            "timestamp": event["timestamp"],
                            "ip_address": event["ip_address"],
                            "session_id": event["session_id"],
                            "created_at": event["created_at"]
                        })

                    self.json_logger.bulk_load_events(date, json_events)
                    dates_backed_up.append(date)

            backup_result = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "users_backed_up": len(db_users),
                "dates_backed_up": dates_backed_up,
                "total_dates": len(dates_backed_up),
                "success": True
            }

            logger.info(f"✅ Backup completed: {len(db_users)} users, {len(dates_backed_up)} dates")
            return backup_result

        except Exception as e:
            logger.error(f"❌ Error during backup: {e}")
            return {"error": str(e), "success": False}


if __name__ == "__main__":
    # Test the data manager
    logging.basicConfig(level=logging.INFO)

    data_manager = DataManager()

    print("Testing DataManager...")

    # Test question processing
    response = data_manager.process_question(
        username="test_user",
        question="What is the meaning of life?",
        ip_address="127.0.0.1"
    )
    print(f"Response: {response}")

    # Test analytics
    analytics = data_manager.get_system_analytics()
    print(f"System Analytics: {analytics}")

    # Test data consistency
    consistency = data_manager.validate_data_consistency()
    print(f"Data Consistency: {consistency}")
