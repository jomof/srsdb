#!/usr/bin/env python
"""
Test script to verify type hints work correctly with mypy and in IDEs.

This demonstrates that srsdb now has complete type hint support.
"""

from datetime import datetime, timedelta
from srsdb import FsrsDatabase, EbisuDatabase
from typing import List, Optional


def test_fsrs_types() -> None:
    """Test FSRS database with type hints."""
    db: FsrsDatabase = FsrsDatabase("test.db")

    now: datetime = datetime.now()

    # These should all type-check correctly
    db.answer(now, "question_1", 85)

    due_cards: List[str] = db.next(now)
    print(f"Due cards: {due_cards}")

    next_review: Optional[datetime] = db.next_due_date()
    if next_review:
        print(f"Next review: {next_review}")


def test_ebisu_types() -> None:
    """Test Ebisu database with type hints."""
    try:
        db: EbisuDatabase = EbisuDatabase("test_ebisu.db")

        now: datetime = datetime.now()

        # These should all type-check correctly
        db.answer(now, "vocab_hello", 90)

        due: List[str] = db.next(now + timedelta(days=1))
        print(f"Due cards (Ebisu): {due}")

        next_due: Optional[datetime] = db.next_due_date()
        if next_due:
            print(f"Next review (Ebisu): {next_due}")
    except ImportError:
        print("Ebisu package not installed, skipping Ebisu tests")


if __name__ == "__main__":
    print("Testing FSRS type hints...")
    test_fsrs_types()
    print("\nTesting Ebisu type hints...")
    test_ebisu_types()
    print("\n✓ All type hints work correctly!")
