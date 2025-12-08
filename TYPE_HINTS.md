# Type Hints Documentation

This document describes the comprehensive type hint support added to srsdb.

## What Was Added

### 1. PEP 561 Compliance

The package now includes a `py.typed` marker file in the `srsdb/` directory, which signals to type checkers that this package supports type hints. This enables:

- Full type checking support in IDEs (VS Code, PyCharm, etc.)
- Static analysis with mypy, pyright, and other type checkers
- Better autocomplete and inline documentation

### 2. Enhanced Docstrings

All public methods now have comprehensive docstrings with:

- **Typed Parameters**: Every parameter is documented with its type
  ```python
  Args:
      now (datetime): The time that the question was answered.
      question_key (str): Unique identifier for the question.
      correct (int): Value from 0-100 indicating correctness.
  ```

- **Return Types**: All return values are explicitly typed
  ```python
  Returns:
      List[str]: List of question keys in chronological order.
  ```

- **Examples**: Practical usage examples for each method
  ```python
  Example:
      >>> from datetime import datetime
      >>> db.answer(datetime.now(), "spanish_hello", 85)
  ```

- **Exceptions**: Documented exceptions that may be raised
  ```python
  Raises:
      ValueError: If correct is not between 0 and 100.
  ```

### 3. Complete Type Annotations

All methods now have complete type annotations:

```python
def __init__(self, database_file: str) -> None: ...
def answer(self, now: datetime, question_key: str, correct: int) -> None: ...
def next(self, now: datetime) -> List[str]: ...
def next_due_date(self) -> Optional[datetime]: ...
```

### 4. Type Checker Compatibility

The code now passes mypy type checking with assertions to handle internal state:

```python
self._open()
assert self._conn is not None  # _open() ensures connection exists
cursor = self._conn.cursor()
```

## How to Use

### In Your IDE

Most modern IDEs will automatically detect the type hints:

```python
from srsdb import FsrsDatabase
from datetime import datetime

db = FsrsDatabase("my.db")  # IDE knows db is FsrsDatabase
db.answer(datetime.now(), "card1", 85)  # IDE validates parameters
due = db.next(datetime.now())  # IDE knows due is List[str]
```

### With Type Checkers

Run mypy to validate your code:

```bash
# Install mypy
pip install mypy

# Check your code
mypy your_script.py
```

Example output:
```bash
$ mypy test_type_hints.py
Success: no issues found in 1 source file
```

### In Python REPL

Get detailed help with type information:

```python
>>> from srsdb import FsrsDatabase
>>> help(FsrsDatabase.answer)
Help on function answer in module srsdb.fsrs_database:

answer(self, now: datetime.datetime, question_key: str, correct: int) -> None
    Records the result of the user answering a question using FSRS algorithm.

    Args:
        now (datetime): The time that the question was answered.
        question_key (str): Unique identifier for the question.
        correct (int): Value from 0-100 indicating correctness.
    ...
```

## Benefits for Integration

### 1. Better IDE Experience

- **Autocomplete**: IDEs can suggest valid methods and parameters
- **Type Checking**: Catch errors before running code
- **Inline Documentation**: See parameter types and descriptions while coding

### 2. Safer Code

Type hints help catch common mistakes:

```python
# This will be flagged by type checkers:
db.answer("not a datetime", "card1", "not an int")  # ❌ Wrong types

# This is correct:
db.answer(datetime.now(), "card1", 85)  # ✓ Correct types
```

### 3. Better Documentation

The enhanced docstrings make it easy to understand how to use the library:

```python
>>> import inspect
>>> print(inspect.signature(FsrsDatabase.answer))
(self, now: datetime.datetime, question_key: str, correct: int) -> None
```

## Example: Type-Safe Code

```python
from datetime import datetime, timedelta
from srsdb import FsrsDatabase
from typing import List, Optional

def study_session(db: FsrsDatabase, now: datetime) -> int:
    """
    Conduct a study session and return the number of cards reviewed.

    Type hints ensure this function is used correctly.
    """
    due_cards: List[str] = db.next(now)

    for card_id in due_cards:
        # Simulate answering (in real code, get from user)
        correctness: int = 75
        db.answer(now, card_id, correctness)

    return len(due_cards)

# Usage
db: FsrsDatabase = FsrsDatabase("study.db")
cards_reviewed: int = study_session(db, datetime.now())
print(f"Reviewed {cards_reviewed} cards")
```

## Package Distribution

The type information is included in the distributed package via `MANIFEST.in`:

```
# Include type information for PEP 561
recursive-include srsdb py.typed
```

This means users who install via pip will automatically get full type hint support.

## Testing Type Hints

A test script is provided to verify type hints work correctly:

```bash
python test_type_hints.py
```

This demonstrates that:
- Type annotations are correct
- Methods work as documented
- Type checkers can validate usage

## Continuous Integration

Type checking is integrated into the GitHub Actions CI/CD pipeline:

- **Automated mypy checks** run on every push and pull request
- The `srsdb/` package is type-checked with mypy
- Type errors will fail the build (ensuring type safety)

You can run the same checks locally:

```bash
# Run mypy with the project configuration
mypy

# Or specify the package explicitly
mypy srsdb/

# Run in strict mode for maximum safety
mypy --strict srsdb/
```

### mypy Configuration

The project includes a `mypy.ini` configuration file with sensible defaults:

```ini
[mypy]
files = srsdb/
python_version = 3.8
ignore_missing_imports = True
```

This ensures consistent type checking across development and CI environments.

## References

- [PEP 561 – Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [mypy Documentation](https://mypy.readthedocs.io/)
