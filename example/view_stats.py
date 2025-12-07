#!/usr/bin/env python3
"""
View statistics from the example databases.
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def view_fsrs_stats():
    """Display statistics from FSRS example database."""
    db_path = os.path.join(os.path.dirname(__file__), "fsrs.db")

    if not os.path.exists(db_path):
        print("❌ fsrs.db not found. Run generate_examples.py first.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("FSRS Database Statistics")
    print("=" * 60)

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_cards,
            AVG(difficulty) as avg_difficulty,
            AVG(stability) as avg_stability,
            AVG(reps) as avg_reps,
            SUM(lapses) as total_lapses
        FROM fsrs_cards
    """)
    stats = cursor.fetchone()

    print("\n📊 Overall Statistics:")
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Average difficulty: {stats['avg_difficulty']:.2f}")
    print(f"  Average stability: {stats['avg_stability']:.2f} days")
    print(f"  Average reviews per card: {stats['avg_reps']:.1f}")
    print(f"  Total lapses: {stats['total_lapses']}")

    # Card details
    print("\n📇 Card Details:")
    cursor.execute("""
        SELECT question_key, difficulty, stability, reps, lapses, state
        FROM fsrs_cards
        ORDER BY stability DESC
    """)

    print(f"  {'Card':<30} {'Diff':>6} {'Stab':>8} {'Reps':>6} {'Lapses':>8} {'State':>8}")
    print("  " + "-" * 76)
    for row in cursor.fetchall():
        state_names = {0: 'New', 1: 'Learning', 2: 'Review', 3: 'Relearn'}
        state_name = state_names.get(row['state'], 'Unknown')
        print(f"  {row['question_key']:<30} {row['difficulty']:>6.2f} "
              f"{row['stability']:>8.1f} {row['reps']:>6} {row['lapses']:>8} "
              f"{state_name:>8}")

    # Review history
    cursor.execute("SELECT COUNT(*) as count FROM fsrs_reviews")
    review_count = cursor.fetchone()['count']
    print(f"\n📝 Total Reviews: {review_count}")

    conn.close()


def view_ebisu_stats():
    """Display statistics from Ebisu example database."""
    db_path = os.path.join(os.path.dirname(__file__), "ebisu.db")

    if not os.path.exists(db_path):
        print("❌ ebisu.db not found. Run generate_examples.py first.")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("Ebisu Database Statistics")
    print("=" * 60)

    # Overall stats
    cursor.execute("""
        SELECT
            COUNT(*) as total_cards,
            AVG(alpha) as avg_alpha,
            AVG(beta) as avg_beta,
            AVG(t) as avg_half_life,
            AVG(total_reviews) as avg_reviews
        FROM ebisu_cards
    """)
    stats = cursor.fetchone()

    print("\n📊 Overall Statistics:")
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Average alpha: {stats['avg_alpha']:.2f}")
    print(f"  Average beta: {stats['avg_beta']:.2f}")
    print(f"  Average half-life: {stats['avg_half_life']:.1f} hours ({stats['avg_half_life']/24:.1f} days)")
    print(f"  Average reviews per card: {stats['avg_reviews']:.1f}")

    # Card details
    print("\n📇 Card Details:")
    cursor.execute("""
        SELECT question_key, alpha, beta, t, total_reviews
        FROM ebisu_cards
        ORDER BY t DESC
    """)

    print(f"  {'Card':<30} {'Alpha':>8} {'Beta':>8} {'Half-life (h)':>15} {'Reviews':>10}")
    print("  " + "-" * 81)
    for row in cursor.fetchall():
        print(f"  {row['question_key']:<30} {row['alpha']:>8.2f} {row['beta']:>8.2f} "
              f"{row['t']:>15.1f} {row['total_reviews']:>10}")

    # Review history
    cursor.execute("SELECT COUNT(*) as count FROM ebisu_reviews")
    review_count = cursor.fetchone()['count']
    print(f"\n📝 Total Reviews: {review_count}")

    # Recall probability distribution
    cursor.execute("""
        SELECT
            AVG(recall_probability) as avg_recall,
            MIN(recall_probability) as min_recall,
            MAX(recall_probability) as max_recall
        FROM ebisu_reviews
        WHERE recall_probability IS NOT NULL
    """)
    recall_stats = cursor.fetchone()
    print(f"\n🧠 Recall Probability Stats:")
    print(f"  Average: {recall_stats['avg_recall']:.3f}")
    print(f"  Min: {recall_stats['min_recall']:.3f}")
    print(f"  Max: {recall_stats['max_recall']:.3f}")

    conn.close()


def main():
    """Display statistics from both databases."""
    view_fsrs_stats()
    view_ebisu_stats()

    print("\n" + "=" * 60)
    print("✨ Use generate_examples.py to regenerate databases")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
