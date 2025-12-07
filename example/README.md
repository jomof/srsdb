# Example Databases

This directory contains example databases demonstrating the FSRS and Ebisu implementations.

## Files

- **`fsrs.db`** - Example FSRS database with Spanish vocabulary learning
- **`ebisu.db`** - Example Ebisu database with Python programming concepts
- **`generate_examples.py`** - Script to regenerate the example databases

## Generating Examples

To regenerate the example databases:

```bash
cd example
python generate_examples.py
```

This will:
1. Delete existing `fsrs.db` and `ebisu.db` files
2. Create new databases with realistic learning scenarios
3. Populate them with review history over simulated time periods

## FSRS Database Contents

**Scenario**: Learning Spanish vocabulary over 15 days

- **10 vocabulary cards** (hello, goodbye, please, thank you, etc.)
- **Multiple review sessions** at days 1, 4, 7, and 15
- **Realistic correctness scores** showing learning progression
- **Demonstrates**:
  - Initial learning with varying success rates
  - Review scheduling based on difficulty
  - Improvement over time
  - FSRS stability and difficulty tracking

### Example Queries

```bash
# View all cards and their current state
sqlite3 example/fsrs.db "SELECT question_key, difficulty, stability, reps, lapses FROM fsrs_cards;"

# View review history
sqlite3 example/fsrs.db "SELECT question_key, review_time, rating FROM fsrs_reviews ORDER BY review_time;"

# Check cards due on a specific date
sqlite3 example/fsrs.db "SELECT question_key, due_date FROM fsrs_cards WHERE due_date <= '2024-01-20' ORDER BY due_date;"
```

## Ebisu Database Contents

**Scenario**: Learning Python programming concepts over 20 days

- **10 programming concept cards** (lists, dicts, functions, classes, etc.)
- **Multiple review sessions** at days 1, 2, 5, 10, and 20
- **Variable difficulty** showing some concepts are harder than others
- **Demonstrates**:
  - Bayesian belief updating
  - Half-life tracking
  - Adaptive scheduling based on recall probability
  - Progressive mastery of difficult concepts

### Example Queries

```bash
# View all cards and their Bayesian models
sqlite3 example/ebisu.db "SELECT question_key, alpha, beta, t, total_reviews FROM ebisu_cards;"

# View review history with recall probabilities
sqlite3 example/ebisu.db "SELECT question_key, review_time, correctness, recall_probability FROM ebisu_reviews ORDER BY review_time;"

# Check average half-life
sqlite3 example/ebisu.db "SELECT AVG(t) as avg_half_life_hours, AVG(t)/24 as avg_half_life_days FROM ebisu_cards;"
```

## Exploring with VS Code

If you have the SQLite Viewer extension installed:

1. Open the example directory in VS Code
2. Click on `fsrs.db` or `ebisu.db` to open the SQLite viewer
3. Browse tables and data visually

## Exploring with sqlite3 CLI

```bash
# Open FSRS database
sqlite3 example/fsrs.db

# List tables
.tables

# View schema
.schema fsrs_cards

# Query data
SELECT * FROM fsrs_cards;

# Exit
.quit
```

## Use Cases

These example databases are useful for:

- 📖 **Learning** - Understanding how SRS algorithms work
- 🧪 **Testing** - Trying out queries and analysis
- 📊 **Visualization** - Creating graphs of learning progress
- 🔬 **Research** - Comparing FSRS vs Ebisu behavior
- 🎓 **Education** - Teaching spaced repetition concepts

## Notes

- Times are stored in ISO 8601 format
- FSRS uses days for intervals, Ebisu uses hours
- Both databases include complete review history
- Data represents realistic learning scenarios with human-like performance patterns
