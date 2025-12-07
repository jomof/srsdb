# Copilot Instructions for srsdb

## Project Overview
- **srsdb** is a Python implementation of an SQLite-backed database for tracking the state of Spaced Repetition System (SRS) learning for individual items.
- The main abstraction is `SrsDatabase`, which provides a unified interface for SRS operations, with pluggable backends (e.g., FSRS, Ebisu).

## Key Components
- **SrsDatabase**: Main interface. Handles database file management, schema setup, and SRS operations.
  - `answer(now, question_key, correct)`: Record an answer event. `correct` is 0-100 (degree of correctness).
  - `next(now)`: Returns questions due as of `now`, ordered by due date.
  - `next_due_date()`: Returns the next due date for any question.
- **FsrsDatabase**: Implements `SrsDatabase` using the `fsrs` library.
- **EbisuDatabase**: Implements `SrsDatabase` using the Ebisu algorithm.
- **Tests**: `FsrsDatabaseTests` and `EbisuDatabaseTests` provide unittests for their respective implementations.

## Developer Workflows
- **Testing**: Run unittests for each backend implementation. (Test runner details TBD; see test files for entry points.)
- **Schema Management**: The database auto-creates required tables if missing, and tolerates unrelated tables.
- **Extensibility**: To add a new SRS backend, subclass `SrsDatabase` and implement the required methods.

## Project Conventions
- `correct` values are always 0-100, mapped internally to backend-specific formats.
- All time-based operations accept a `now` parameter for testability (not hardcoded to system time).
- Database schema is backend-specific but must not interfere with unrelated tables in the SQLite file.

## Key Files
- `README.md`: High-level overview and API documentation.
- (Source files for `SrsDatabase`, `FsrsDatabase`, `EbisuDatabase`, and their tests should be referenced here when available.)

## Integration Points
- **fsrs**: External library for SRS logic in `FsrsDatabase`.
- **Ebisu**: External library for SRS logic in `EbisuDatabase`.

## Example Usage
```python
# Example: Recording an answer
srs = SrsDatabase('my.db')
srs.answer(now, 'question1', 80)
due_questions = srs.next(now)
next_due = srs.next_due_date()
```

---

**Update this file as new backends, workflows, or conventions are introduced.**
