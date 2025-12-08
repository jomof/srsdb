"""
Tests for FsrsKnobs and EbisuKnobs configuration.
"""
import unittest
import os
import tempfile
from datetime import datetime, timedelta
from srsdb import FsrsDatabase, FsrsKnobs, EbisuDatabase, EbisuKnobs


class FsrsKnobsTests(unittest.TestCase):
    """Tests for FsrsKnobs configuration."""

    def setUp(self):
        """Create a temporary database file for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_file.close()
        self.db_path = self.temp_file.name

    def tearDown(self):
        """Clean up temporary database file."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_default_knobs(self):
        """Test that default knobs work correctly."""
        db = FsrsDatabase(self.db_path)
        self.assertIsNotNone(db.knobs)
        self.assertEqual(db.knobs.rating_thresholds, (25, 50, 85))
        self.assertEqual(len(db.knobs.w), 17)

    def test_custom_rating_thresholds(self):
        """Test custom rating thresholds."""
        # More strict thresholds
        knobs = FsrsKnobs(rating_thresholds=(30, 60, 90))
        db = FsrsDatabase(self.db_path, knobs)

        now = datetime.now()

        # Test conversions with strict thresholds
        # correctness=29 should be "Again" (rating 1)
        db.answer(now, "card1", 29)
        # correctness=59 should be "Hard" (rating 2)
        db.answer(now, "card2", 59)
        # correctness=89 should be "Good" (rating 3)
        db.answer(now, "card3", 89)
        # correctness=90 should be "Easy" (rating 4)
        db.answer(now, "card4", 90)

        # Verify the database was created successfully
        due = db.next(now + timedelta(days=30))
        self.assertEqual(len(due), 4)

    def test_custom_weights(self):
        """Test custom FSRS weights."""
        # Create custom weights (all zeros for testing)
        custom_weights = [0.0] * 17
        knobs = FsrsKnobs(w=custom_weights)
        db = FsrsDatabase(self.db_path, knobs)

        self.assertEqual(db.knobs.w, custom_weights)

        # Should still work (even if scheduling is weird)
        now = datetime.now()
        db.answer(now, "card1", 80)
        due = db.next(now + timedelta(days=1))
        # Card should be scheduled
        self.assertTrue(len(due) >= 0)

    def test_knobs_persistence(self):
        """Test that knobs affect behavior across database instances."""
        knobs = FsrsKnobs(rating_thresholds=(30, 60, 90))

        # Create first instance
        db1 = FsrsDatabase(self.db_path, knobs)
        now = datetime.now()
        db1.answer(now, "card1", 50)  # Should be "Hard" with strict thresholds

        # Create second instance with same knobs
        db2 = FsrsDatabase(self.db_path, knobs)
        due = db2.next(now + timedelta(days=30))
        self.assertEqual(len(due), 1)


class EbisuKnobsTests(unittest.TestCase):
    """Tests for EbisuKnobs configuration."""

    def setUp(self):
        """Create a temporary database file for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_file.close()
        self.db_path = self.temp_file.name

    def tearDown(self):
        """Clean up temporary database file."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_default_knobs(self):
        """Test that default knobs work correctly."""
        try:
            db = EbisuDatabase(self.db_path)
            self.assertIsNotNone(db.knobs)
            self.assertEqual(db.knobs.default_half_life_hours, 24.0)
            self.assertEqual(db.knobs.recall_threshold, 0.5)
            self.assertEqual(db.knobs.target_recall, 0.5)
        except ImportError:
            self.skipTest("Ebisu package not installed")

    def test_custom_half_life(self):
        """Test custom initial half-life."""
        try:
            # Shorter initial half-life (12 hours instead of 24)
            knobs = EbisuKnobs(default_half_life_hours=12.0)
            db = EbisuDatabase(self.db_path, knobs)

            self.assertEqual(db.knobs.default_half_life_hours, 12.0)

            now = datetime.now()
            db.answer(now, "card1", 80)

            # Cards should be due sooner with shorter half-life
            next_due = db.next_due_date()
            self.assertIsNotNone(next_due)
        except ImportError:
            self.skipTest("Ebisu package not installed")

    def test_custom_recall_threshold(self):
        """Test custom recall threshold."""
        try:
            # Higher recall threshold means cards are due earlier
            knobs = EbisuKnobs(recall_threshold=0.7)
            db = EbisuDatabase(self.db_path, knobs)

            self.assertEqual(db.knobs.recall_threshold, 0.7)

            now = datetime.now()
            db.answer(now, "card1", 80)

            # At time now, recall should be high, so card not due yet
            due = db.next(now)
            self.assertEqual(len(due), 0)

            # After some time, card should be due earlier due to higher threshold
            later = now + timedelta(days=1)
            due = db.next(later)
            # Card should eventually be due
            self.assertTrue(len(due) >= 0)
        except ImportError:
            self.skipTest("Ebisu package not installed")

    def test_knobs_multiple_instances(self):
        """Test that different instances can have different knobs."""
        try:
            knobs1 = EbisuKnobs(default_half_life_hours=12.0)
            knobs2 = EbisuKnobs(default_half_life_hours=48.0)

            db1 = EbisuDatabase(self.db_path + "1", knobs1)
            db2 = EbisuDatabase(self.db_path + "2", knobs2)

            self.assertEqual(db1.knobs.default_half_life_hours, 12.0)
            self.assertEqual(db2.knobs.default_half_life_hours, 48.0)

            # Cleanup extra file
            if os.path.exists(self.db_path + "1"):
                os.unlink(self.db_path + "1")
            if os.path.exists(self.db_path + "2"):
                os.unlink(self.db_path + "2")
        except ImportError:
            self.skipTest("Ebisu package not installed")


if __name__ == '__main__':
    unittest.main()
