"""Data repository for persisting books and impressions."""

import json
import os
from typing import List, Optional

from src.models import Book, Impression, StatusHistory


class DataRepository:
    """Repository for managing data persistence."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the repository with a data directory."""
        self.data_dir = data_dir
        self.books_file = os.path.join(data_dir, "books.json")
        self.impressions_file = os.path.join(data_dir, "impressions.json")
        self.status_history_file = os.path.join(data_dir, "status_history.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize files if they don't exist
        if not os.path.exists(self.books_file):
            self._write_json(self.books_file, [])
        if not os.path.exists(self.impressions_file):
            self._write_json(self.impressions_file, [])
        if not os.path.exists(self.status_history_file):
            self._write_json(self.status_history_file, [])

    def _read_json(self, filepath: str) -> list:
        """Read JSON file and return data.

        Raises:
            IOError: If file is corrupted and cannot be recovered
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise IOError(
                f"Data file '{filepath}' is corrupted and cannot be parsed: {str(e)}"
            )
        except FileNotFoundError:
            return []

    def _write_json(self, filepath: str, data: list) -> None:
        """Write data to JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_books(self, books: List[Book]) -> None:
        """Save books to file."""
        data = [book.to_dict() for book in books]
        self._write_json(self.books_file, data)

    def load_books(self) -> List[Book]:
        """Load books from file.

        Raises:
            IOError: If books file is corrupted
        """
        data = self._read_json(self.books_file)
        return [Book.from_dict(item) for item in data]

    def save_impressions(self, impressions: List[Impression]) -> None:
        """Save impressions to file."""
        data = [impression.to_dict() for impression in impressions]
        self._write_json(self.impressions_file, data)

    def load_impressions(self) -> List[Impression]:
        """Load impressions from file.

        Raises:
            IOError: If impressions file is corrupted
        """
        data = self._read_json(self.impressions_file)
        return [Impression.from_dict(item) for item in data]

    def save_status_history(self, history: List[StatusHistory]) -> None:
        """Save status history to file."""
        data = [h.to_dict() for h in history]
        self._write_json(self.status_history_file, data)

    def load_status_history(self) -> List[StatusHistory]:
        """Load status history from file.

        Raises:
            IOError: If status history file is corrupted
        """
        data = self._read_json(self.status_history_file)
        return [StatusHistory.from_dict(item) for item in data]
