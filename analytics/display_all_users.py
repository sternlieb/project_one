#!/usr/bin/env python3
"""
Display All Users - Simple JSON Query
This script reads the users.json file and displays all users with their details.
"""

import csv
import json
import os
from datetime import datetime


def load_users_data(data_dir="../server/data"):
    """Load users data from users.json file."""
    users_file = os.path.join(data_dir, "users.json")

    if not os.path.exists(users_file):
        print("❌ users.json file not found!")
        return []

    try:
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("users", [])
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")
        return []


def display_users(users):
    """Display users in a formatted table."""
    if not users:
        print("📊 No users found.")
        return

    print("👥 ALL USERS FROM users.json")
    print("=" * 80)
    print(
        f"{'#':<3} {'Username':<20} {'Questions':<10} {'First Seen':<20} {'Last Seen':<20}"
    )
    print("-" * 80)

    for i, user in enumerate(users, 1):
        username = user.get("username", "N/A")
        total_questions = user.get("total_questions", 0)
        first_seen = (
            user.get("first_seen", "")[:19] if user.get("first_seen") else "N/A"
        )
        last_seen = user.get("last_seen", "")[:19] if user.get("last_seen") else "N/A"

        print(
            f"{i:<3} {username:<20} {total_questions:<10} {first_seen:<20} {last_seen:<20}"
        )

    print("-" * 80)
    print(f"📊 Total Users: {len(users)}")


def save_to_csv(users, filename="all_users.csv"):
    """Save users data to CSV file."""
    if not users:
        print("❌ No users to export.")
        return False

    try:
        output_path = os.path.join(os.path.dirname(__file__), filename)

        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "username",
                "total_questions",
                "first_seen",
                "last_seen",
                "created_at",
                "updated_at",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write user data
            for user in users:
                writer.writerow(
                    {
                        "username": user.get("username", ""),
                        "total_questions": user.get("total_questions", 0),
                        "first_seen": user.get("first_seen", ""),
                        "last_seen": user.get("last_seen", ""),
                        "created_at": user.get("created_at", ""),
                        "updated_at": user.get("updated_at", ""),
                    }
                )

        print(f"✅ Users exported to: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")
        return False


def main():
    """Main function to run the user display query."""
    print("🚀 Loading All Users from JSON")
    print("=" * 50)

    # Load users data
    users = load_users_data()

    if not users:
        return

    # Display users
    display_users(users)

    # Save to CSV
    print(f"\n📄 Exporting users to CSV...")
    save_to_csv(users)

    print(f"\n✅ Query complete! Found {len(users)} users.")


if __name__ == "__main__":
    main()
