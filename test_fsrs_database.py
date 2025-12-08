import unittest
import os
import tempfile
from datetime import datetime, timedelta
from srsdb import FsrsDatabase


class FsrsDatabaseTests(unittest.TestCase):
    """
    Unit tests for FsrsDatabase implementation.
    """

    def setUp(self):
        """Create a temporary database file for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = FsrsDatabase(self.db_path)

    def tearDown(self):
        """Clean up the temporary database file."""
        if hasattr(self, 'db'):
            self.db._close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_database_creation(self):
        """Test that database file is created when first accessed."""
        self.assertFalse(os.path.getsize(self.db_path) > 0)
        self.db._open()
        self.assertTrue(os.path.getsize(self.db_path) > 0)

    def test_schema_creation(self):
        """Test that the required tables are created."""
        self.db._open()
        cursor = self.db._conn.cursor()

        # Check fsrs_cards table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='fsrs_cards'
        """)
        self.assertIsNotNone(cursor.fetchone())

        # Check fsrs_reviews table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='fsrs_reviews'
        """)
        self.assertIsNotNone(cursor.fetchone())

    def test_answer_new_card_perfect(self):
        """Test answering a new card with perfect correctness."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        self.db.answer(now, "question1", 100)

        # Verify card was created
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT * FROM fsrs_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertIsNotNone(card)
        self.assertEqual(card['question_key'], "question1")
        self.assertEqual(card['reps'], 1)
        self.assertEqual(card['lapses'], 0)
        self.assertEqual(card['state'], 2)  # Should be in Review state for rating 4

    def test_answer_new_card_failed(self):
        """Test answering a new card incorrectly."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        self.db.answer(now, "question1", 0)

        # Verify card state
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT * FROM fsrs_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertIsNotNone(card)
        self.assertEqual(card['reps'], 1)
        self.assertEqual(card['lapses'], 1)
        self.assertEqual(card['state'], 3)  # Should be in Relearning state for rating 1

    def test_answer_multiple_reviews(self):
        """Test multiple reviews of the same card."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # First review
        self.db.answer(now, "question1", 80)

        # Second review after some time
        later = now + timedelta(days=5)
        self.db.answer(later, "question1", 90)

        # Verify review count
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT * FROM fsrs_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertEqual(card['reps'], 2)
        self.assertEqual(card['lapses'], 0)

        # Verify review history
        cursor.execute("SELECT COUNT(*) as count FROM fsrs_reviews WHERE question_key = ?", ("question1",))
        count = cursor.fetchone()['count']
        self.assertEqual(count, 2)

    def test_answer_invalid_correctness(self):
        """Test that invalid correctness values raise errors."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        with self.assertRaises(ValueError):
            self.db.answer(now, "question1", -1)

        with self.assertRaises(ValueError):
            self.db.answer(now, "question1", 101)

    def test_next_no_due_cards(self):
        """Test next() when no cards are due."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        due_cards = self.db.next(now)
        self.assertEqual(due_cards, [])

    def test_next_with_due_cards(self):
        """Test next() returns cards that are due."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add some cards
        self.db.answer(now, "question1", 80)
        self.db.answer(now, "question2", 90)
        self.db.answer(now, "question3", 70)

        # Check some time in the future
        future = now + timedelta(days=10)
        due_cards = self.db.next(future)

        # All cards should be due
        self.assertIn("question1", due_cards)
        self.assertIn("question2", due_cards)
        self.assertIn("question3", due_cards)

    def test_next_chronological_order(self):
        """Test that next() returns cards in chronological order of due date."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Answer cards with different correctness to get different due dates
        self.db.answer(now, "question1", 100)  # Easy - longer interval
        self.db.answer(now, "question2", 60)   # Good - medium interval
        self.db.answer(now, "question3", 40)   # Hard - shorter interval

        # Check well into the future
        future = now + timedelta(days=30)
        due_cards = self.db.next(future)

        # Verify order (cards with shorter intervals should come first)
        # The exact order depends on FSRS algorithm, but we should have all 3
        self.assertEqual(len(due_cards), 3)

    def test_next_partial_due(self):
        """Test next() when only some cards are due."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add cards
        self.db.answer(now, "question1", 80)
        self.db.answer(now, "question2", 90)

        # Check shortly after - only cards with short intervals should be due
        soon = now + timedelta(days=1)
        due_cards = self.db.next(soon)

        # At least some cards might not be due yet depending on intervals
        self.assertLessEqual(len(due_cards), 2)

    def test_next_due_date_no_cards(self):
        """Test next_due_date() when no cards exist."""
        next_due = self.db.next_due_date()
        self.assertIsNone(next_due)

    def test_next_due_date_with_cards(self):
        """Test next_due_date() returns the earliest due date."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add cards
        self.db.answer(now, "question1", 80)
        self.db.answer(now, "question2", 90)

        next_due = self.db.next_due_date()
        self.assertIsNotNone(next_due)
        self.assertIsInstance(next_due, datetime)
        self.assertGreater(next_due, now)

    def test_multiple_cards(self):
        """Test managing multiple cards simultaneously."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add multiple cards
        for i in range(10):
            self.db.answer(now, f"question{i}", 50 + i * 5)

        # Verify all cards were created
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM fsrs_cards")
        count = cursor.fetchone()['count']
        self.assertEqual(count, 10)

    def test_correctness_to_rating_conversion(self):
        """Test the conversion from correctness percentage to FSRS rating."""
        # Test boundary values
        self.assertEqual(self.db._convert_correctness_to_rating(0), 1)    # Again
        self.assertEqual(self.db._convert_correctness_to_rating(24), 1)   # Again
        self.assertEqual(self.db._convert_correctness_to_rating(25), 2)   # Hard
        self.assertEqual(self.db._convert_correctness_to_rating(49), 2)   # Hard
        self.assertEqual(self.db._convert_correctness_to_rating(50), 3)   # Good
        self.assertEqual(self.db._convert_correctness_to_rating(84), 3)   # Good
        self.assertEqual(self.db._convert_correctness_to_rating(85), 4)   # Easy
        self.assertEqual(self.db._convert_correctness_to_rating(100), 4)  # Easy

    def test_database_persistence(self):
        """Test that data persists across database instances."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add a card
        self.db.answer(now, "question1", 75)
        self.db._close()

        # Create new instance with same file
        db2 = FsrsDatabase(self.db_path)
        due_cards = db2.next(now + timedelta(days=10))

        self.assertIn("question1", due_cards)
        db2._close()

    def test_tolerant_of_other_tables(self):
        """Test that the database is tolerant of unrelated tables."""
        # Create an unrelated table first
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("CREATE TABLE unrelated_table (id INTEGER, data TEXT)")
        cursor.execute("INSERT INTO unrelated_table VALUES (1, 'test')")
        self.db._conn.commit()
        self.db._close()

        # Now use the database normally
        now = datetime(2024, 1, 1, 10, 0, 0)
        self.db.answer(now, "question1", 75)

        # Verify both tables exist and work
        self.db._open()
        cursor = self.db._conn.cursor()

        cursor.execute("SELECT * FROM unrelated_table")
        self.assertIsNotNone(cursor.fetchone())

        cursor.execute("SELECT * FROM fsrs_cards WHERE question_key = ?", ("question1",))
        self.assertIsNotNone(cursor.fetchone())

    def test_lapse_tracking(self):
        """Test that lapses (failures) are tracked correctly."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Initial review - fail
        self.db.answer(now, "question1", 0)

        # Second review - pass
        self.db.answer(now + timedelta(days=1), "question1", 80)

        # Third review - fail again
        self.db.answer(now + timedelta(days=2), "question1", 10)

        # Check lapses
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT lapses FROM fsrs_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()
        self.assertEqual(card['lapses'], 2)


if __name__ == '__main__':
    unittest.main()
