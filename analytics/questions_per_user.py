#!/usr/bin/env python3
# force commit
"""
Questions Per User Analytics - JSON Analysis
This script analyzes the JSON log files to provide insights about questions per user.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

# Add the server directory to the Python path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "server"))

try:
    from json_logger import JSONLogger
except ImportError:
    print(
        "❌ Could not import JSONLogger. Make sure you're running from the correct directory."
    )
    sys.exit(1)


class QuestionsPerUserAnalyzer:
    """Analyzes JSON log files to extract user question statistics."""

    def __init__(self, data_dir: str = "../server/data"):
        """
        Initialize the analyzer.

        Args:
            data_dir (str): Path to the data directory containing JSON files
        """
        self.data_dir = os.path.abspath(data_dir)
        self.json_logger = JSONLogger(self.data_dir)

    def get_questions_per_user(self) -> Dict[str, int]:
        """
        Get the total number of questions per user from JSON files.

        Returns:
            Dict[str, int]: Dictionary mapping username to question count
        """
        user_question_counts = defaultdict(int)

        try:
            # Get all available dates with events
            available_dates = self.json_logger.get_available_dates()

            if not available_dates:
                print("📊 No event data found in JSON files.")
                return dict(user_question_counts)

            print(f"📅 Found event data for {len(available_dates)} dates")

            # Process events from all dates
            total_events = 0
            for date in available_dates:
                events = self.json_logger.get_daily_events(date)
                print(f"  {date}: {len(events)} events")

                for event in events:
                    username = event.get("username", "unknown")
                    user_question_counts[username] += 1
                    total_events += 1

            print(f"\n📈 Total events processed: {total_events}")
            return dict(user_question_counts)

        except Exception as e:
            print(f"❌ Error analyzing JSON data: {e}")
            return {}

    def get_users_from_users_file(self) -> Dict[str, Any]:
        """
        Get user data from the users.json file.

        Returns:
            Dict[str, Any]: Dictionary with user statistics
        """
        try:
            users = self.json_logger.get_all_users()

            if not users:
                print("👥 No users found in users.json file.")
                return {}

            user_stats = {}
            for user in users:
                username = user.get("username", "unknown")
                user_stats[username] = {
                    "total_questions": user.get("total_questions", 0),
                    "first_seen": user.get("first_seen", ""),
                    "last_seen": user.get("last_seen", ""),
                    "created_at": user.get("created_at", ""),
                }

            return user_stats

        except Exception as e:
            print(f"❌ Error reading users.json: {e}")
            return {}

    def analyze_user_activity_patterns(self) -> Dict[str, Any]:
        """
        Analyze user activity patterns across time.

        Returns:
            Dict[str, Any]: Analysis results with patterns and insights
        """
        try:
            available_dates = self.json_logger.get_available_dates()
            user_daily_activity = defaultdict(lambda: defaultdict(int))
            user_timestamps = defaultdict(list)

            # Collect activity data
            for date in available_dates:
                events = self.json_logger.get_daily_events(date)

                for event in events:
                    username = event.get("username", "unknown")
                    timestamp = event.get("timestamp", "")

                    user_daily_activity[username][date] += 1
                    if timestamp:
                        user_timestamps[username].append(timestamp)

            # Analyze patterns
            analysis = {
                "user_activity_by_date": dict(user_daily_activity),
                "most_active_days": {},
                "user_streaks": {},
                "peak_hours": {},
                "total_active_days": {},
            }

            for username in user_daily_activity:
                # Most active day
                daily_counts = user_daily_activity[username]
                most_active_day = max(daily_counts.items(), key=lambda x: x[1])
                analysis["most_active_days"][username] = {
                    "date": most_active_day[0],
                    "questions": most_active_day[1],
                }

                # Total active days
                analysis["total_active_days"][username] = len(daily_counts)

                # Peak hours analysis (if timestamps available)
                if username in user_timestamps:
                    hours = []
                    for ts in user_timestamps[username]:
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            hours.append(dt.hour)
                        except:
                            continue

                    if hours:
                        hour_counts = Counter(hours)
                        peak_hour = hour_counts.most_common(1)[0]
                        analysis["peak_hours"][username] = {
                            "hour": peak_hour[0],
                            "questions_count": peak_hour[1],
                            "percentage": round(peak_hour[1] / len(hours) * 100, 1),
                        }

            return analysis

        except Exception as e:
            print(f"❌ Error analyzing user activity patterns: {e}")
            return {}

    def generate_report(self) -> str:
        """
        Generate a comprehensive user analytics report.

        Returns:
            str: Formatted report string
        """
        print("🔍 Analyzing JSON data for user question statistics...\n")

        # Get data from both sources
        questions_per_user = self.get_questions_per_user()
        users_file_data = self.get_users_from_users_file()
        activity_patterns = self.analyze_user_activity_patterns()

        if not questions_per_user and not users_file_data:
            return "❌ No data found in JSON files."

        # Generate report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("📊 QUESTIONS PER USER ANALYTICS REPORT (FROM JSON DATA)")
        report_lines.append("=" * 80)
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Questions per user from events
        if questions_per_user:
            report_lines.append("📈 QUESTIONS PER USER (FROM EVENT LOGS)")
            report_lines.append("-" * 50)

            # Sort by question count (descending)
            sorted_users = sorted(
                questions_per_user.items(), key=lambda x: x[1], reverse=True
            )

            for rank, (username, count) in enumerate(sorted_users, 1):
                report_lines.append(f"{rank:2d}. {username:<20} {count:>6} questions")

            report_lines.append("")
            report_lines.append(f"🎯 Total Users: {len(sorted_users)}")
            report_lines.append(
                f"🎯 Total Questions: {sum(questions_per_user.values())}"
            )
            report_lines.append(
                f"🎯 Average Questions per User: {sum(questions_per_user.values()) / len(sorted_users):.1f}"
            )
            report_lines.append("")

        # Users file data comparison
        if users_file_data:
            report_lines.append("👥 USER STATISTICS (FROM USERS.JSON)")
            report_lines.append("-" * 50)

            sorted_users_file = sorted(
                users_file_data.items(),
                key=lambda x: x[1]["total_questions"],
                reverse=True,
            )

            for rank, (username, data) in enumerate(sorted_users_file, 1):
                report_lines.append(
                    f"{rank:2d}. {username:<20} {data['total_questions']:>6} questions "
                    f"(First: {data['first_seen'][:10] if data['first_seen'] else 'N/A'})"
                )

            report_lines.append("")

        # Activity patterns
        if activity_patterns:
            report_lines.append("📅 USER ACTIVITY PATTERNS")
            report_lines.append("-" * 50)

            # Most active days
            if activity_patterns.get("most_active_days"):
                report_lines.append("🔥 Most Active Days per User:")
                for username, day_data in activity_patterns["most_active_days"].items():
                    report_lines.append(
                        f"   {username:<20} {day_data['date']} ({day_data['questions']} questions)"
                    )
                report_lines.append("")

            # Peak hours
            if activity_patterns.get("peak_hours"):
                report_lines.append("⏰ Peak Hours per User:")
                for username, hour_data in activity_patterns["peak_hours"].items():
                    hour_12 = hour_data["hour"] % 12
                    ampm = "AM" if hour_data["hour"] < 12 else "PM"
                    if hour_12 == 0:
                        hour_12 = 12
                    report_lines.append(
                        f"   {username:<20} {hour_12:2d}:00 {ampm} "
                        f"({hour_data['percentage']}% of activity)"
                    )
                report_lines.append("")

            # Active days count
            if activity_patterns.get("total_active_days"):
                report_lines.append("📊 Total Active Days per User:")
                sorted_active_days = sorted(
                    activity_patterns["total_active_days"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
                for username, days in sorted_active_days:
                    report_lines.append(f"   {username:<20} {days:>3} days")
                report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def export_to_csv(self, filename: str = "questions_per_user.csv") -> bool:
        """
        Export user question statistics to CSV file.

        Args:
            filename (str): Output CSV filename

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            questions_per_user = self.get_questions_per_user()
            users_file_data = self.get_users_from_users_file()

            if not questions_per_user and not users_file_data:
                print("❌ No data to export.")
                return False

            # Combine data from both sources
            all_users = set(questions_per_user.keys()) | set(users_file_data.keys())

            csv_lines = []
            csv_lines.append(
                "username,questions_from_events,questions_from_users_file,first_seen,last_seen"
            )

            for username in sorted(all_users):
                event_count = questions_per_user.get(username, 0)
                user_data = users_file_data.get(username, {})
                file_count = user_data.get("total_questions", 0)
                first_seen = (
                    user_data.get("first_seen", "")[:19]
                    if user_data.get("first_seen")
                    else ""
                )
                last_seen = (
                    user_data.get("last_seen", "")[:19]
                    if user_data.get("last_seen")
                    else ""
                )

                csv_lines.append(
                    f'"{username}",{event_count},{file_count},"{first_seen}","{last_seen}"'
                )

            # Write to file
            output_path = os.path.join(os.path.dirname(__file__), filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(csv_lines))

            print(f"✅ Data exported to: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False


def main():
    """Main function to run the analysis."""
    print("🚀 Starting Questions Per User Analysis")
    print("=" * 50)

    # Initialize analyzer
    analyzer = QuestionsPerUserAnalyzer()

    # Generate and print report
    report = analyzer.generate_report()
    print(report)

    # Export to CSV
    print("\n📄 Exporting data to CSV...")
    analyzer.export_to_csv()

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
