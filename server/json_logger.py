"""
JSON Logger Module

Handles JSON file operations for users and daily events logging.
"""

import json
import os
import asyncio
import aiofiles
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class JSONLogger:
    """Manages JSON file operations for users and events logging."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the JSONLogger.

        Args:
            data_dir (str): Directory to store JSON files
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.events_dir = os.path.join(data_dir, "events")
        self._file_locks = {}
        self._lock = Lock()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        for directory in [self.data_dir, self.events_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"📁 Created directory: {directory}")

    def _get_file_lock(self, filepath: str) -> Lock:
        """Get or create a file-specific lock."""
        with self._lock:
            if filepath not in self._file_locks:
                self._file_locks[filepath] = Lock()
            return self._file_locks[filepath]

    def _load_users_file(self) -> Dict[str, Any]:
        """Load the users.json file or create empty structure."""
        if not os.path.exists(self.users_file):
            return {
                "schema_version": "1.0",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_users": 0,
                "users": []
            }

        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"❌ Error loading users file: {e}")
            return {
                "schema_version": "1.0",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_users": 0,
                "users": []
            }

    def _save_users_file(self, data: Dict[str, Any]):
        """Save the users.json file with proper locking."""
        file_lock = self._get_file_lock(self.users_file)

        with file_lock:
            try:
                # Update metadata
                data["last_updated"] = datetime.now(timezone.utc).isoformat()
                data["total_users"] = len(data.get("users", []))

                # Write to temporary file first, then rename (atomic operation)
                temp_file = f"{self.users_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Atomic rename
                os.rename(temp_file, self.users_file)
                logger.debug(f"💾 Users file saved successfully")

            except Exception as e:
                logger.error(f"❌ Error saving users file: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise

    def log_user(self, user_data: Dict[str, Any]):
        """
        Log or update a user in the users.json file.

        Args:
            user_data (Dict[str, Any]): User data dictionary
        """
        try:
            users_data = self._load_users_file()
            users = users_data.get("users", [])

            # Find existing user
            user_index = None
            for i, user in enumerate(users):
                if user.get("username") == user_data.get("username"):
                    user_index = i
                    break

            if user_index is not None:
                # Update existing user
                users[user_index] = user_data
                logger.debug(f"👤 Updated user in JSON: {user_data.get('username')}")
            else:
                # Add new user
                users.append(user_data)
                logger.info(f"👤 Added new user to JSON: {user_data.get('username')}")

            users_data["users"] = users
            self._save_users_file(users_data)

        except Exception as e:
            logger.error(f"❌ Error logging user to JSON: {e}")
            # Don't raise - this is secondary storage

    async def log_user_async(self, user_data: Dict[str, Any]):
        """Async version of log_user."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.log_user, user_data)

    def _get_events_file_path(self, date: str) -> str:
        """Get the file path for events on a specific date."""
        return os.path.join(self.events_dir, f"events_{date}.json")

    def _load_events_file(self, date: str) -> Dict[str, Any]:
        """Load events file for a specific date or create empty structure."""
        events_file = self._get_events_file_path(date)

        if not os.path.exists(events_file):
            return {
                "date": date,
                "schema_version": "1.0",
                "total_events": 0,
                "events": []
            }

        try:
            with open(events_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"❌ Error loading events file for {date}: {e}")
            return {
                "date": date,
                "schema_version": "1.0",
                "total_events": 0,
                "events": []
            }

    def _save_events_file(self, date: str, data: Dict[str, Any]):
        """Save events file for a specific date with proper locking."""
        events_file = self._get_events_file_path(date)
        file_lock = self._get_file_lock(events_file)

        with file_lock:
            try:
                # Update metadata
                data["total_events"] = len(data.get("events", []))

                # Write to temporary file first, then rename (atomic operation)
                temp_file = f"{events_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Atomic rename
                os.rename(temp_file, events_file)
                logger.debug(f"💾 Events file saved for {date}")

            except Exception as e:
                logger.error(f"❌ Error saving events file for {date}: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise

    def log_event(self, event_data: Dict[str, Any]):
        """
        Log an event to the appropriate daily JSON file.

        Args:
            event_data (Dict[str, Any]): Event data dictionary
        """
        try:
            # Extract date from timestamp
            timestamp = event_data.get("timestamp", "")
            if timestamp:
                # Parse ISO timestamp and get date
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date = dt.date().isoformat()
            else:
                # Use current date as fallback
                date = datetime.now(timezone.utc).date().isoformat()

            # Load existing events for this date
            events_data = self._load_events_file(date)
            events = events_data.get("events", [])

            # Add new event
            events.append(event_data)
            events_data["events"] = events

            # Save updated events file
            self._save_events_file(date, events_data)

            logger.debug(f"📝 Event logged to JSON for {date}: Event ID {event_data.get('id')}")

        except Exception as e:
            logger.error(f"❌ Error logging event to JSON: {e}")
            # Don't raise - this is secondary storage

    async def log_event_async(self, event_data: Dict[str, Any]):
        """Async version of log_event."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.log_event, event_data)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from the JSON file."""
        try:
            users_data = self._load_users_file()
            return users_data.get("users", [])
        except Exception as e:
            logger.error(f"❌ Error getting users from JSON: {e}")
            return []

    def get_daily_events(self, date: str) -> List[Dict[str, Any]]:
        """
        Get all events for a specific date from JSON.

        Args:
            date (str): Date in YYYY-MM-DD format

        Returns:
            List[Dict[str, Any]]: List of events
        """
        try:
            events_data = self._load_events_file(date)
            return events_data.get("events", [])
        except Exception as e:
            logger.error(f"❌ Error getting events from JSON for {date}: {e}")
            return []

    def get_available_dates(self) -> List[str]:
        """Get list of dates that have event files."""
        try:
            if not os.path.exists(self.events_dir):
                return []

            dates = []
            for filename in os.listdir(self.events_dir):
                if filename.startswith("events_") and filename.endswith(".json"):
                    # Extract date from filename: events_2024-10-04.json -> 2024-10-04
                    date = filename[7:-5]  # Remove "events_" prefix and ".json" suffix
                    dates.append(date)

            return sorted(dates)

        except Exception as e:
            logger.error(f"❌ Error getting available dates: {e}")
            return []

    def export_all_data(self) -> Dict[str, Any]:
        """Export all data (users and all events) to a single dictionary."""
        try:
            result = {
                "export_timestamp": datetime.now(timezone.utc).isoformat(),
                "users": self.get_all_users(),
                "events_by_date": {}
            }

            # Get all available dates and their events
            for date in self.get_available_dates():
                result["events_by_date"][date] = self.get_daily_events(date)

            return result

        except Exception as e:
            logger.error(f"❌ Error exporting all data: {e}")
            return {}

    def bulk_load_users(self, users_list: List[Dict[str, Any]]):
        """
        Bulk load multiple users into the JSON file.

        Args:
            users_list (List[Dict[str, Any]]): List of user dictionaries
        """
        try:
            users_data = {
                "schema_version": "1.0",
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_users": len(users_list),
                "users": users_list
            }

            self._save_users_file(users_data)
            logger.info(f"📥 Bulk loaded {len(users_list)} users to JSON")

        except Exception as e:
            logger.error(f"❌ Error bulk loading users: {e}")
            raise

    def bulk_load_events(self, date: str, events_list: List[Dict[str, Any]]):
        """
        Bulk load multiple events for a specific date.

        Args:
            date (str): Date in YYYY-MM-DD format
            events_list (List[Dict[str, Any]]): List of event dictionaries
        """
        try:
            events_data = {
                "date": date,
                "schema_version": "1.0",
                "total_events": len(events_list),
                "events": events_list
            }

            self._save_events_file(date, events_data)
            logger.info(f"📥 Bulk loaded {len(events_list)} events to JSON for {date}")

        except Exception as e:
            logger.error(f"❌ Error bulk loading events for {date}: {e}")
            raise


if __name__ == "__main__":
    # Test the JSON logger
    logging.basicConfig(level=logging.INFO)

    json_logger = JSONLogger()

    print("Testing JSONLogger...")

    # Test user logging
    test_user = {
        "id": 1,
        "username": "test_user",
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "total_questions": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    json_logger.log_user(test_user)
    print("Logged test user")

    # Test event logging
    test_event = {
        "id": 1,
        "user_id": 1,
        "username": "test_user",
        "question": "What is 2+2?",
        "answer": "Four!",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip_address": "127.0.0.1",
        "session_id": "sess_123"
    }

    json_logger.log_event(test_event)
    print("Logged test event")

    # Test data retrieval
    users = json_logger.get_all_users()
    print(f"Users in JSON: {len(users)}")

    today = datetime.now(timezone.utc).date().isoformat()
    events = json_logger.get_daily_events(today)
    print(f"Events today: {len(events)}")
