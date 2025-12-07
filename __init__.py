"""
SRSDB - Spaced Repetition System Database

A Python library for managing SRS (Spaced Repetition System) learning data
using SQLite with support for different SRS algorithms.
"""

from .srs_database import SrsDatabase
from .fsrs_database import FsrsDatabase

__version__ = "0.1.0"
__all__ = ["SrsDatabase", "FsrsDatabase"]
