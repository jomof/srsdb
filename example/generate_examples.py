#!/usr/bin/env python3
"""
Generate example databases for FSRS and Ebisu implementations.
These databases are created for demonstration and testing purposes.
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from srsdb import FsrsDatabase, EbisuDatabase


def generate_fsrs_example():
    """Generate example FSRS database with realistic learning scenarios."""

    db_path = os.path.join(os.path.dirname(__file__), "fsrs.db")

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    db = FsrsDatabase(db_path)

    # Simulate a learning journey over 30 days
    start_date = datetime(2024, 1, 1, 9, 0, 0)

    # Day 1: Initial learning of vocabulary
    print("FSRS Example Database")
    print("=" * 50)
    print("\n📅 Day 1: Initial Learning")

    day1 = start_date
    vocabulary = {
        "spanish_hello": ("hola", 95),
        "spanish_goodbye": ("adiós", 90),
        "spanish_please": ("por favor", 60),
        "spanish_thankyou": ("gracias", 85),
        "spanish_yes": ("sí", 100),
        "spanish_no": ("no", 100),
        "spanish_water": ("agua", 75),
        "spanish_food": ("comida", 55),
        "spanish_house": ("casa", 80),
        "spanish_friend": ("amigo", 90),
    }

    for card_id, (word, correctness) in vocabulary.items():
        db.answer(day1, card_id, correctness)
        print(f"  Learned: {card_id:25s} ({word:15s}) - {correctness}% correct")

    # Day 2: Review struggling cards
    print("\n📅 Day 2: First Review")
    day2 = start_date + timedelta(days=1)
    due_cards = db.next(day2)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        # Improved performance on review
        db.answer(day2, card, 80)
        print(f"  Reviewed: {card:25s} - 80% correct (improved!)")

    # Day 4: Another review session
    print("\n📅 Day 4: Second Review")
    day4 = start_date + timedelta(days=3)
    due_cards = db.next(day4)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        # Most cards doing well, one struggling
        correctness = 90 if "please" not in card else 65
        db.answer(day4, card, correctness)
        status = "struggling" if correctness < 70 else "good"
        print(f"  Reviewed: {card:25s} - {correctness}% correct ({status})")

    # Day 7: Week review
    print("\n📅 Day 7: Week Review")
    day7 = start_date + timedelta(days=6)
    due_cards = db.next(day7)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        # Strong performance
        db.answer(day7, card, 95)
        print(f"  Reviewed: {card:25s} - 95% correct (mastering!)")

    # Day 15: Two-week check
    print("\n📅 Day 15: Two-Week Check")
    day15 = start_date + timedelta(days=14)
    due_cards = db.next(day15)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        db.answer(day15, card, 100)
        print(f"  Reviewed: {card:25s} - 100% correct (mastered!)")

    # Show final statistics
    print("\n📊 Final Statistics")
    db._open()
    cursor = db._conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_cards,
            AVG(reps) as avg_reviews,
            AVG(stability) as avg_stability,
            SUM(lapses) as total_lapses
        FROM fsrs_cards
    """)
    stats = cursor.fetchone()
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Average reviews per card: {stats['avg_reviews']:.1f}")
    print(f"  Average stability (days): {stats['avg_stability']:.1f}")
    print(f"  Total lapses: {stats['total_lapses']}")

    next_due = db.next_due_date()
    if next_due:
        days_until = (next_due - day15).days
        print(f"  Next review due in: {days_until} days")

    db._close()
    print(f"\n✅ FSRS database created: {db_path}")


def generate_ebisu_example():
    """Generate example Ebisu database with realistic learning scenarios."""

    db_path = os.path.join(os.path.dirname(__file__), "ebisu.db")

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    db = EbisuDatabase(db_path)

    # Simulate learning programming concepts over time
    start_date = datetime(2024, 1, 1, 10, 0, 0)

    print("\n" + "=" * 50)
    print("Ebisu Example Database")
    print("=" * 50)
    print("\n📅 Day 1: Learning Programming Concepts")

    day1 = start_date
    concepts = {
        "python_list": ("list data structure", 90),
        "python_dict": ("dictionary/hash map", 85),
        "python_function": ("function definition", 95),
        "python_class": ("class and objects", 70),
        "python_loop": ("for/while loops", 100),
        "python_conditional": ("if/else statements", 100),
        "python_exception": ("try/except handling", 60),
        "python_decorator": ("decorator pattern", 45),
        "python_generator": ("generator functions", 55),
        "python_comprehension": ("list comprehensions", 75),
    }

    for card_id, (concept, correctness) in concepts.items():
        db.answer(day1, card_id, correctness)
        print(f"  Learned: {card_id:25s} ({concept:25s}) - {correctness}% correct")

    # Day 2: Quick review of difficult concepts
    print("\n📅 Day 2: Review Difficult Concepts")
    day2 = start_date + timedelta(days=1)

    difficult_cards = ["python_decorator", "python_exception", "python_generator", "python_class"]
    for card in difficult_cards:
        db.answer(day2, card, 75)
        print(f"  Reviewed: {card:25s} - 75% correct (improving)")

    # Day 5: Check what's due
    print("\n📅 Day 5: Regular Review Session")
    day5 = start_date + timedelta(days=4)
    due_cards = db.next(day5)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        # Variable performance based on difficulty
        if "decorator" in card or "generator" in card:
            correctness = 80
            status = "progressing"
        else:
            correctness = 95
            status = "strong"
        db.answer(day5, card, correctness)
        print(f"  Reviewed: {card:25s} - {correctness}% correct ({status})")

    # Day 10: Major review
    print("\n📅 Day 10: Comprehensive Review")
    day10 = start_date + timedelta(days=9)
    due_cards = db.next(day10)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        db.answer(day10, card, 90)
        print(f"  Reviewed: {card:25s} - 90% correct (solid)")

    # Day 20: Long-term retention check
    print("\n📅 Day 20: Long-term Retention")
    day20 = start_date + timedelta(days=19)
    due_cards = db.next(day20)
    print(f"  Cards due: {len(due_cards)}")

    for card in due_cards:
        db.answer(day20, card, 95)
        print(f"  Reviewed: {card:25s} - 95% correct (retained!)")

    # Show final statistics
    print("\n📊 Final Statistics")
    db._open()
    cursor = db._conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) as total_cards,
            AVG(total_reviews) as avg_reviews,
            AVG(t) as avg_half_life
        FROM ebisu_cards
    """)
    stats = cursor.fetchone()
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Average reviews per card: {stats['avg_reviews']:.1f}")
    print(f"  Average half-life (hours): {stats['avg_half_life']:.1f}")

    next_due = db.next_due_date()
    if next_due:
        hours_until = (next_due - day20).total_seconds() / 3600
        print(f"  Next review due in: {hours_until:.1f} hours")

    db._close()
    print(f"\n✅ Ebisu database created: {db_path}")


def main():
    """Generate both example databases."""
    generate_fsrs_example()
    generate_ebisu_example()

    print("\n" + "=" * 50)
    print("✨ Example databases created successfully!")
    print("=" * 50)
    print("\nYou can explore these databases using:")
    print("  - SQLite viewer extension in VS Code")
    print("  - sqlite3 command line tool")
    print("  - Any SQLite browser")


if __name__ == "__main__":
    main()
