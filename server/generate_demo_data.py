"""
Demo Data Generator

Generates 20 demo users with 100 events each per day for 3 days (Oct 1-3, 2025).
Creates identical data in both SQLite database and JSON files.
"""

import random
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

from data_manager import DataManager
from response_handler import response_handler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DemoDataGenerator:
    """Generate realistic demo data for the Q&A application."""

    def __init__(self):
        """Initialize the demo data generator."""
        self.data_manager = DataManager()

        # Demo usernames
        self.usernames = [
            "alice_wonder", "bob_builder", "charlie_brown", "diana_prince",
            "ethan_hunt", "fiona_green", "george_lucas", "helen_troy",
            "ivan_terrible", "jane_doe", "kevin_hart", "lucy_diamond",
            "mike_tyson", "nina_simone", "oscar_wilde", "penny_lane",
            "quincy_jones", "ruby_red", "steve_jobs", "tina_turner"
        ]

        # Demo questions pool (realistic user questions)
        self.questions = [
            "What is the weather like today?",
            "How do I learn programming?",
            "What's the best way to cook pasta?",
            "Can you help me with math homework?",
            "What is artificial intelligence?",
            "How do I start a business?",
            "What's the meaning of life?",
            "How do I lose weight quickly?",
            "What are the best movies this year?",
            "How do I fix my computer?",
            "What is blockchain technology?",
            "How do I learn a new language?",
            "What's the capital of France?",
            "How do I make friends?",
            "What is machine learning?",
            "How do I save money?",
            "What's the best exercise routine?",
            "How do I improve my memory?",
            "What is quantum physics?",
            "How do I become more confident?",
            "What's the best way to study?",
            "How do I write a resume?",
            "What is cryptocurrency?",
            "How do I stop procrastinating?",
            "What's the secret to happiness?",
            "How do I learn to draw?",
            "What is climate change?",
            "How do I start investing?",
            "What's the best programming language?",
            "How do I improve my writing?",
            "What is the universe made of?",
            "How do I become successful?",
            "What's the best diet plan?",
            "How do I overcome anxiety?",
            "What is the stock market?",
            "How do I learn guitar?",
            "What's the future of technology?",
            "How do I improve my sleep?",
            "What is democracy?",
            "How do I become more creative?",
            "What's the best way to travel?",
            "How do I manage stress?",
            "What is evolution?",
            "How do I build confidence?",
            "What's the meaning of success?",
            "How do I learn photography?",
            "What is renewable energy?",
            "How do I improve communication?",
            "What's the best career advice?",
            "How do I stay motivated?",
            "What is virtual reality?",
            "How do I learn coding fast?",
            "What's the secret to longevity?",
            "How do I become a leader?",
            "What is social media impact?",
            "How do I improve my skills?",
            "What's the best way to exercise?",
            "How do I learn new things?",
            "What is sustainable living?",
            "How do I build relationships?",
            "What's the future of work?",
            "How do I overcome fear?",
            "What is mindfulness?",
            "How do I improve productivity?",
            "What's the best time management?",
            "How do I learn from mistakes?",
            "What is emotional intelligence?",
            "How do I find my purpose?",
            "What's the key to innovation?",
            "How do I develop habits?",
            "What is work-life balance?",
            "How do I handle criticism?",
            "What's the power of networking?",
            "How do I stay focused?",
            "What is personal growth?",
            "How do I overcome challenges?",
            "What's the importance of education?",
            "How do I build wealth?",
            "What is digital transformation?",
            "How do I improve decision making?",
            "What's the future of AI?",
            "How do I develop patience?",
            "What is sustainable development?",
            "How do I improve teamwork?",
            "What's the best learning method?",
            "How do I handle change?",
            "What is cultural diversity?",
            "How do I build trust?",
            "What's the impact of globalization?",
            "How do I develop empathy?",
            "What is data science?",
            "How do I improve problem solving?",
            "What's the role of technology?",
            "How do I build resilience?",
            "What is ethical behavior?",
            "How do I improve listening skills?",
            "What's the future of education?",
            "How do I develop leadership?",
            "What is environmental protection?",
            "How do I improve adaptability?",
            "What's the importance of diversity?",
            "How do I build self-confidence?"
        ]

        # IP addresses pool for demo
        self.ip_addresses = [
            "192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13",
            "10.0.0.15", "10.0.0.16", "10.0.0.17", "10.0.0.18",
            "172.16.0.20", "172.16.0.21", "127.0.0.1", "192.168.100.5",
            "10.1.1.25", "172.20.0.30", "192.168.0.100", "10.0.1.50"
        ]

    def generate_demo_data(self) -> Dict[str, Any]:
        """
        Generate complete demo data for 3 days.

        Returns:
            Dict[str, Any]: Generation summary
        """
        try:
            logger.info("🚀 Starting demo data generation...")

            # Define the 3 demo days (Oct 1-3, 2025)
            demo_dates = [
                datetime(2025, 10, 1, tzinfo=timezone.utc),
                datetime(2025, 10, 2, tzinfo=timezone.utc),
                datetime(2025, 10, 3, tzinfo=timezone.utc)
            ]

            total_events = 0
            events_by_date = {}

            # Generate data for each date
            for date in demo_dates:
                date_str = date.date().isoformat()
                logger.info(f"📅 Generating data for {date_str}...")

                day_events = self._generate_day_events(date)
                events_by_date[date_str] = len(day_events)
                total_events += len(day_events)

                logger.info(f"✅ Generated {len(day_events)} events for {date_str}")

            # Force backup to JSON to ensure consistency
            backup_result = self.data_manager.backup_to_json()

            summary = {
                "generation_complete": True,
                "total_users": len(self.usernames),
                "total_events": total_events,
                "events_by_date": events_by_date,
                "demo_dates": [d.date().isoformat() for d in demo_dates],
                "backup_result": backup_result
            }

            logger.info(f"🎉 Demo data generation complete!")
            logger.info(f"📊 Summary: {len(self.usernames)} users, {total_events} total events")

            return summary

        except Exception as e:
            logger.error(f"❌ Error generating demo data: {e}")
            raise

    def _generate_day_events(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Generate 100 events for each user for a specific day.

        Args:
            date (datetime): The date to generate events for

        Returns:
            List[Dict[str, Any]]: List of generated events
        """
        events = []

        for username in self.usernames:
            user_events = self._generate_user_day_events(username, date)
            events.extend(user_events)

        return events

    def _generate_user_day_events(self, username: str, date: datetime) -> List[Dict[str, Any]]:
        """
        Generate 100 events for a specific user on a specific day.

        Args:
            username (str): Username to generate events for
            date (datetime): Date to generate events for

        Returns:
            List[Dict[str, Any]]: List of events for this user
        """
        events = []

        # Generate 100 events throughout the day
        for event_num in range(100):
            # Random time during the day (spread across 24 hours)
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)

            event_time = date.replace(
                hour=random_hour,
                minute=random_minute,
                second=random_second
            )

            # Random question from the pool
            question = random.choice(self.questions)

            # Random IP address
            ip_address = random.choice(self.ip_addresses)

            # Generate session ID (users might have multiple sessions per day)
            session_num = (event_num // 10) + 1  # New session every ~10 events
            session_id = f"sess_{username}_{date.strftime('%Y%m%d')}_{session_num:02d}"

            # Get a random answer using the existing response handler
            answer = response_handler.get_random_response()

            # Log event directly to database with historical timestamp
            try:
                # Log event directly to database with custom timestamp
                event_id = self.data_manager.db_manager.log_event(
                    username=username,
                    question=question,
                    answer=answer,
                    ip_address=ip_address,
                    session_id=session_id,
                    timestamp=event_time.isoformat()
                )

                # Also log to JSON with historical data
                user_info = self.data_manager.db_manager.get_user_stats(username)
                if user_info:
                    self.data_manager.json_logger.log_user(user_info)

                    event_data = {
                        "id": event_id,
                        "user_id": user_info.get("id"),
                        "username": username,
                        "question": question,
                        "answer": answer,
                        "timestamp": event_time.isoformat(),
                        "ip_address": ip_address,
                        "session_id": session_id,
                        "created_at": event_time.isoformat()
                    }

                    self.data_manager.json_logger.log_event(event_data)

                events.append({
                    "event_id": event_id,
                    "username": username,
                    "question": question,
                    "answer": answer,
                    "timestamp": event_time.isoformat(),
                    "ip_address": ip_address,
                    "session_id": session_id
                })

            except Exception as e:
                logger.error(f"❌ Error creating event for {username}: {e}")
                continue

        logger.info(f"👤 Generated {len(events)} events for user {username} on {date.date()}")
        return events


    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of the demo data.

        Returns:
            Dict[str, Any]: Summary report
        """
        try:
            # Get analytics from data manager
            analytics = self.data_manager.get_system_analytics()

            # Get consistency report
            consistency = self.data_manager.validate_data_consistency()

            report = {
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "system_analytics": analytics,
                "data_consistency": consistency,
                "demo_config": {
                    "users_count": len(self.usernames),
                    "events_per_user_per_day": 100,
                    "total_days": 3,
                    "date_range": "2025-10-01 to 2025-10-03",
                    "total_expected_events": len(self.usernames) * 100 * 3
                }
            }

            return report

        except Exception as e:
            logger.error(f"❌ Error generating summary report: {e}")
            return {"error": str(e)}


def main():
    """Main function to run demo data generation."""
    print("=" * 60)
    print("🎯 Q&A Demo Data Generator")
    print("=" * 60)
    print(f"📋 Configuration:")
    print(f"   • Users: 20 demo users")
    print(f"   • Events per user per day: 100")
    print(f"   • Days: 3 (October 1-3, 2025)")
    print(f"   • Total events: 6,000")
    print(f"   • Storage: SQLite + JSON files")
    print("=" * 60)

    # Confirm generation
    confirmation = input("\n🤔 Generate demo data? This will add 6,000 events to your database. (y/N): ")
    if confirmation.lower() not in ['y', 'yes']:
        print("❌ Demo data generation cancelled.")
        return

    try:
        # Create generator and run
        generator = DemoDataGenerator()

        print("\n🚀 Starting generation...")
        result = generator.generate_demo_data()

        print("\n" + "=" * 60)
        print("✅ DEMO DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"👥 Users created: {result['total_users']}")
        print(f"📝 Total events: {result['total_events']}")
        print(f"📅 Events by date:")
        for date, count in result['events_by_date'].items():
            print(f"   • {date}: {count} events")

        # Generate summary report
        print("\n📊 Generating summary report...")
        report = generator.generate_summary_report()

        if "error" not in report:
            db_stats = report.get("system_analytics", {}).get("database_stats", {})
            print(f"\n📈 Final Statistics:")
            print(f"   • Database users: {db_stats.get('total_users', 0)}")
            print(f"   • Database events: {db_stats.get('total_events', 0)}")

            consistency = report.get("data_consistency", {})
            user_consistency = consistency.get("user_consistency", {})
            print(f"   • JSON backup users: {user_consistency.get('total_json_users', 0)}")
            print(f"   • Data consistency: {'✅ OK' if consistency.get('overall_health', {}).get('users_consistent') else '❌ Issues detected'}")

        print("\n🎉 Your Q&A application now has realistic demo data!")
        print("💡 You can now test analytics, user tracking, and data export features.")
        print("\n📂 Check the following files:")
        print(f"   • Database: server/data/qa_database.db")
        print(f"   • Users JSON: server/data/users.json")
        print(f"   • Events JSON: server/data/events/events_2025-10-*.json")

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        logger.exception("Full error details:")


if __name__ == "__main__":
    main()
