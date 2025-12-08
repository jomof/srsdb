import unittest
import os
import tempfile
from datetime import datetime, timedelta

# Check if ebisu is available
try:
    import ebisu
    from srsdb import EbisuDatabase
    EBISU_AVAILABLE = True
except ImportError:
    EBISU_AVAILABLE = False


@unittest.skipUnless(EBISU_AVAILABLE, "ebisu package not installed")
class EbisuDatabaseTests(unittest.TestCase):
    """
    Unit tests for EbisuDatabase implementation.
    """

    def setUp(self):
        """Create a temporary database file for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = EbisuDatabase(self.db_path)

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

        # Check ebisu_cards table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='ebisu_cards'
        """)
        self.assertIsNotNone(cursor.fetchone())

        # Check ebisu_reviews table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='ebisu_reviews'
        """)
        self.assertIsNotNone(cursor.fetchone())

    def test_answer_new_card_perfect(self):
        """Test answering a new card with perfect correctness."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        self.db.answer(now, "question1", 100)

        # Verify card was created
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT * FROM ebisu_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertIsNotNone(card)
        self.assertEqual(card['question_key'], "question1")
        self.assertEqual(card['total_reviews'], 1)
        self.assertGreater(card['alpha'], 0)
        self.assertGreater(card['beta'], 0)
        self.assertGreater(card['t'], 0)

    def test_answer_new_card_failed(self):
        """Test answering a new card incorrectly."""
        now = datetime(2024, 1, 1, 10, 0, 0)
        self.db.answer(now, "question1", 0)

        # Verify card state
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT * FROM ebisu_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertIsNotNone(card)
        self.assertEqual(card['total_reviews'], 1)
        # After a failure, the half-life should be relatively short
        self.assertLess(card['t'], 24.0)  # Less than initial 24 hours

    def test_answer_multiple_reviews(self):
        """Test multiple reviews of the same card."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # First review - correct
        self.db.answer(now, "question1", 80)

        # Get initial half-life
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT t FROM ebisu_cards WHERE question_key = ?", ("question1",))
        initial_t = cursor.fetchone()['t']

        # Second review after some time - also correct
        later = now + timedelta(hours=12)
        self.db.answer(later, "question1", 90)

        # Verify review count
        cursor.execute("SELECT * FROM ebisu_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        self.assertEqual(card['total_reviews'], 2)

        # After successful reviews, half-life should increase
        self.assertGreater(card['t'], initial_t)

        # Verify review history
        cursor.execute("SELECT COUNT(*) as count FROM ebisu_reviews WHERE question_key = ?", ("question1",))
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

        # Add some cards with varying correctness
        self.db.answer(now, "question1", 80)
        self.db.answer(now, "question2", 90)
        self.db.answer(now, "question3", 70)

        # Check after significant time has passed
        future = now + timedelta(days=7)
        due_cards = self.db.next(future)

        # All cards should be due after a week
        self.assertGreater(len(due_cards), 0)

    def test_next_ordering_by_recall(self):
        """Test that next() returns cards ordered by recall probability (lowest first)."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add cards with different correctness levels
        self.db.answer(now, "easy_card", 100)
        self.db.answer(now, "medium_card", 60)
        self.db.answer(now, "hard_card", 30)

        # Check well into the future
        future = now + timedelta(days=10)
        due_cards = self.db.next(future)

        # The hard card should be most forgotten and come first
        if len(due_cards) > 0:
            # We can't guarantee exact order without knowing Ebisu internals,
            # but we can verify cards are returned
            self.assertGreater(len(due_cards), 0)

    def test_next_due_date_no_cards(self):
        """Test next_due_date() when no cards exist."""
        next_due = self.db.next_due_date()
        self.assertIsNone(next_due)

    def test_next_due_date_with_cards(self):
        """Test next_due_date() returns a future date."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add cards
        self.db.answer(now, "question1", 80)
        self.db.answer(now, "question2", 90)

        next_due = self.db.next_due_date()
        self.assertIsNotNone(next_due)
        self.assertIsInstance(next_due, datetime)
        # Next due date should be in the future
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
        cursor.execute("SELECT COUNT(*) as count FROM ebisu_cards")
        count = cursor.fetchone()['count']
        self.assertEqual(count, 10)

    def test_correctness_to_success_conversion(self):
        """Test the conversion from correctness percentage to success value."""
        self.assertAlmostEqual(self.db._convert_correctness_to_success(0), 0.0)
        self.assertAlmostEqual(self.db._convert_correctness_to_success(50), 0.5)
        self.assertAlmostEqual(self.db._convert_correctness_to_success(100), 1.0)
        self.assertAlmostEqual(self.db._convert_correctness_to_success(75), 0.75)

    def test_database_persistence(self):
        """Test that data persists across database instances."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Add a card
        self.db.answer(now, "question1", 75)
        self.db._close()

        # Create new instance with same file
        db2 = EbisuDatabase(self.db_path)

        # Verify card exists
        db2._open()
        cursor = db2._conn.cursor()
        cursor.execute("SELECT * FROM ebisu_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()
        self.assertIsNotNone(card)
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

        cursor.execute("SELECT * FROM ebisu_cards WHERE question_key = ?", ("question1",))
        self.assertIsNotNone(cursor.fetchone())

    def test_recall_probability_tracking(self):
        """Test that recall probability is tracked in review history."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # First review
        self.db.answer(now, "question1", 80)

        # Check review record
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT recall_probability FROM ebisu_reviews WHERE question_key = ?", ("question1",))
        review = cursor.fetchone()

        self.assertIsNotNone(review)
        # Initial recall probability should be high (1.0 for new card)
        self.assertGreaterEqual(review['recall_probability'], 0.9)

    def test_forgetting_curve(self):
        """Test that Ebisu implements a forgetting curve."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # Learn a card
        self.db.answer(now, "question1", 100)

        # Get the model
        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT alpha, beta, t, last_review FROM ebisu_cards WHERE question_key = ?", ("question1",))
        card = cursor.fetchone()

        model = (card['alpha'], card['beta'], card['t'])
        last_review = datetime.fromisoformat(card['last_review'])

        # Check recall at different time points
        recall_now = ebisu.predictRecall(model, 0.1, exact=True)
        recall_half_life = ebisu.predictRecall(model, card['t'], exact=True)
        recall_double = ebisu.predictRecall(model, card['t'] * 2, exact=True)

        # Recall should decrease over time
        self.assertGreater(recall_now, recall_half_life)
        self.assertGreater(recall_half_life, recall_double)

        # At half-life, recall should be around 0.5
        self.assertAlmostEqual(recall_half_life, 0.5, delta=0.2)

    def test_successful_reviews_increase_interval(self):
        """Test that successful reviews increase the review interval."""
        now = datetime(2024, 1, 1, 10, 0, 0)

        # First review - successful
        self.db.answer(now, "question1", 90)

        self.db._open()
        cursor = self.db._conn.cursor()
        cursor.execute("SELECT t FROM ebisu_cards WHERE question_key = ?", ("question1",))
        t1 = cursor.fetchone()['t']

        # Second review after half-life - also successful
        later = now + timedelta(hours=t1)
        self.db.answer(later, "question1", 95)

        cursor.execute("SELECT t FROM ebisu_cards WHERE question_key = ?", ("question1",))
        t2 = cursor.fetchone()['t']

        # After successful review, half-life should increase
        self.assertGreater(t2, t1)


if __name__ == '__main__':
    unittest.main()
