#!/usr/bin/env python3
"""
Example usage of FsrsDatabase for spaced repetition learning.
"""

from datetime import datetime, timedelta
from fsrs_database import FsrsDatabase


def main():
    # Create a database instance
    db = FsrsDatabase("example.db")

    # Simulate learning session starting January 1, 2024
    now = datetime(2024, 1, 1, 10, 0, 0)

    print("=== Initial Learning Session ===")
    print(f"Time: {now}\n")

    # Answer some questions
    print("Answering question1 with 85% correctness (Easy)")
    db.answer(now, "question1", 85)

    print("Answering question2 with 60% correctness (Good)")
    db.answer(now, "question2", 60)

    print("Answering question3 with 20% correctness (Again/Failed)")
    db.answer(now, "question3", 20)

    # Check what's due now
    print(f"\n=== Cards due at {now} ===")
    due_now = db.next(now)
    print(f"Due cards: {due_now}")

    # Check next due date
    next_due = db.next_due_date()
    print(f"\nNext due date: {next_due}")

    # Advance time by 2 days
    now = now + timedelta(days=2)
    print(f"\n=== Time advanced to {now} ===")

    # Check what's due
    due_cards = db.next(now)
    print(f"Cards due: {due_cards}")

    # Review the due cards
    if due_cards:
        print(f"\nReviewing {len(due_cards)} card(s):")
        for card in due_cards:
            # Simulate answering with varying correctness
            correctness = 75
            print(f"  - {card}: {correctness}% correct")
            db.answer(now, card, correctness)

    # Advance time by 5 more days
    now = now + timedelta(days=5)
    print(f"\n=== Time advanced to {now} ===")

    # Check what's due
    due_cards = db.next(now)
    print(f"Cards due: {due_cards}")

    # Show next due date
    next_due = db.next_due_date()
    print(f"Next due date: {next_due}")

    print("\n=== Session Complete ===")
    print("Database saved to example.db")

    # Clean up
    db._close()


if __name__ == "__main__":
    main()
