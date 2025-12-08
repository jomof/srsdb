#!/usr/bin/env python
"""
Example demonstrating custom configuration with FsrsKnobs and EbisuKnobs.
"""

from datetime import datetime, timedelta
from srsdb import FsrsDatabase, FsrsKnobs, EbisuDatabase, EbisuKnobs


def demo_fsrs_knobs():
    """Demonstrate FsrsKnobs customization."""
    print("=" * 60)
    print("FSRS Knobs Demo")
    print("=" * 60)

    # Default configuration
    print("\n1. Default Configuration:")
    db_default = FsrsDatabase("demo_default.db")
    print(f"   Rating thresholds: {db_default.knobs.rating_thresholds}")
    print(f"   Number of weights: {len(db_default.knobs.w)}")

    # Strict configuration (higher thresholds)
    print("\n2. Strict Configuration:")
    strict_knobs = FsrsKnobs(rating_thresholds=(30, 60, 90))
    db_strict = FsrsDatabase("demo_strict.db", strict_knobs)
    print(f"   Rating thresholds: {db_strict.knobs.rating_thresholds}")

    # Test with a card
    now = datetime.now()
    db_default.answer(now, "card1", 50)
    db_strict.answer(now, "card1", 50)

    print(f"\n   Correctness=50:")
    print(f"   - Default: treated as 'Good' (threshold 50)")
    print(f"   - Strict:  treated as 'Hard' (threshold 60)")

    # Cleanup
    import os
    os.unlink("demo_default.db")
    os.unlink("demo_strict.db")


def demo_ebisu_knobs():
    """Demonstrate EbisuKnobs customization."""
    print("\n" + "=" * 60)
    print("Ebisu Knobs Demo")
    print("=" * 60)

    try:
        # Default configuration
        print("\n1. Default Configuration:")
        db_default = EbisuDatabase("demo_ebisu_default.db")
        print(f"   Initial half-life: {db_default.knobs.default_half_life_hours} hours")
        print(f"   Recall threshold: {db_default.knobs.recall_threshold}")

        # Fast review configuration
        print("\n2. Fast Review Configuration:")
        fast_knobs = EbisuKnobs(default_half_life_hours=12.0)
        db_fast = EbisuDatabase("demo_ebisu_fast.db", fast_knobs)
        print(f"   Initial half-life: {db_fast.knobs.default_half_life_hours} hours")

        # Conservative configuration
        print("\n3. Conservative Configuration:")
        conservative_knobs = EbisuKnobs(recall_threshold=0.7)
        db_conservative = EbisuDatabase("demo_ebisu_conservative.db", conservative_knobs)
        print(f"   Recall threshold: {db_conservative.knobs.recall_threshold}")
        print("   (Cards are due when recall < 70% instead of < 50%)")

        # Cleanup
        import os
        for db_file in ["demo_ebisu_default.db", "demo_ebisu_fast.db", "demo_ebisu_conservative.db"]:
            if os.path.exists(db_file):
                os.unlink(db_file)

    except ImportError:
        print("\n   [Skipped: Ebisu package not installed]")
        print("   Install with: pip install ebisu")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "Knobs Configuration Demo" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")

    demo_fsrs_knobs()
    demo_ebisu_knobs()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
FsrsKnobs allows you to customize:
  - rating_thresholds: How correctness maps to ratings
  - w: FSRS algorithm weight parameters

EbisuKnobs allows you to customize:
  - default_half_life_hours: Initial review interval
  - recall_threshold: When cards are considered due
  - target_recall: Scheduling target

Use these to tune the algorithm to your learning style!
    """)


if __name__ == "__main__":
    main()
