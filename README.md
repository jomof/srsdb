# srsdb
Python implementation of SQLite database that tracks state of SRS learning of individual items.

Main interface is SrsDatabase
  public constructor(databaseFile): # just remembers the database file path

  private open(): # Opens or creates the database. If the database exists, but doesn't have the tables needed, then creates those tables. Is tolerant of unrelated tables that might be in the database. The schema of the tables is
  particular to the underlying srs library.

  public answer(now, question_key: str, correct: number): # First calls open().  Records the result of the user answering a question. 'correct' is a value from 0-100. 0 means completely wrong, 100 means completely correct. Everything in between is a degress of correctness. Internally, it's converted to an appropriate value for the underlying srs system.
  'now' is the time that the question was answered. It doesn't have to be the real 'now' for the purposes of testing.

  public next(now): str # First calls open(). Returns the questions, in chronological order of due date, that are due as of 'now'.

  public next_due_date(): # First calls open(). Returns the date/time of the next moment that a question is due.

FsrsDatabase # An implementation of SrsDatabase that uses the 'fsrs' library.
FsrsDatabaseTests # Unittests for FsrsDatabase

EbisuDatabase # An implementation of SrsDatabase backed by Ebisu
EbisuDatabaseTests # Unittests for EbisuDatabase




