"""
Response Handler Module

This module handles loading responses from JSON file and returning random responses.
"""

import json
import random
import os
from typing import List, Optional


class ResponseHandler:
    """Handles loading and serving random responses from a JSON file."""

    def __init__(self, json_file_path: str = "responses.json"):
        """
        Initialize the ResponseHandler with a JSON file.

        Args:
            json_file_path (str): Path to the JSON file containing responses
        """
        self.json_file_path = json_file_path
        self.responses: List[str] = []
        self.load_responses()

    def load_responses(self) -> None:
        """
        Load responses from the JSON file.

        Raises:
            FileNotFoundError: If the JSON file is not found
            ValueError: If the JSON file format is invalid
        """
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, self.json_file_path)

            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if 'responses' not in data:
                raise ValueError("JSON file must contain a 'responses' key")

            self.responses = data['responses']

            if not self.responses:
                raise ValueError("Responses list cannot be empty")

            print(f"✅ Loaded {len(self.responses)} responses from {self.json_file_path}")

        except FileNotFoundError:
            print(f"❌ Error: Could not find {self.json_file_path}")
            # Fallback responses if file is not found
            self.responses = [
                "I'm having trouble finding my response file.",
                "Something went wrong with my responses.",
                "Please check my configuration."
            ]

        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format in {self.json_file_path}: {e}")
            self.responses = ["There's an error in my response configuration."]

        except ValueError as e:
            print(f"❌ Error: {e}")
            self.responses = ["My responses are not configured properly."]

    def get_random_response(self) -> str:
        """
        Get a random response from the loaded responses.

        Returns:
            str: A random response string
        """
        if not self.responses:
            return "I don't have any responses available right now."

        return random.choice(self.responses)

    def reload_responses(self) -> None:
        """
        Reload responses from the JSON file.
        Useful if the JSON file has been updated.
        """
        print("🔄 Reloading responses from JSON file...")
        self.load_responses()

    def get_all_responses(self) -> List[str]:
        """
        Get all available responses.

        Returns:
            List[str]: List of all response strings
        """
        return self.responses.copy()

    def get_response_count(self) -> int:
        """
        Get the number of available responses.

        Returns:
            int: Number of responses
        """
        return len(self.responses)


# Create a global instance for easy importing
response_handler = ResponseHandler()


def get_random_answer() -> str:
    """
    Convenience function to get a random response.

    Returns:
        str: A random response string
    """
    return response_handler.get_random_response()


if __name__ == "__main__":
    # Test the response handler
    print("Testing Response Handler...")
    print("-" * 40)

    handler = ResponseHandler()
    print(f"Number of responses loaded: {handler.get_response_count()}")
    print()

    print("Sample random responses:")
    for i in range(5):
        print(f"{i+1}. {handler.get_random_response()}")

    print("-" * 40)
    print("All available responses:")
    for i, response in enumerate(handler.get_all_responses(), 1):
        print(f"{i}. {response}")
