"""Status management service for books."""

from datetime import datetime, timezone
from typing import List, Optional

from src.models import Book, StatusHistory
from src.repository import DataRepository


class StatusService:
    """Service for managing book reading status."""

    def __init__(self, repository: DataRepository):
        """Initialize the status service.

        Args:
            repository: DataRepository instance for data persistence
        """
        self.repository = repository
        self.status_history: List[StatusHistory] = self._load_status_history()

    def _load_status_history(self) -> List[StatusHistory]:
        """Load status history from repository."""
        try:
            return self.repository.load_status_history()
        except (FileNotFoundError, IOError):
            return []

    def set_status(self, book_id: str, new_status: str) -> Book:
        """Set the reading status of a book.

        Args:
            book_id: ID of the book
            new_status: New status (積読/読書中/読了)

        Returns:
            Updated Book instance

        Raises:
            ValueError: If book not found or invalid status
        """
        books = self.repository.load_books()
        book = None
        for b in books:
            if b.id == book_id:
                book = b
                break

        if not book:
            raise ValueError(f"Book with ID {book_id} not found")

        valid_statuses = ["積読", "読書中", "読了"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")

        old_status = book.status
        book.status = new_status
        book.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Record status change in history
        history = StatusHistory(
            book_id=book_id, old_status=old_status, new_status=new_status
        )
        self.status_history.append(history)

        # Save updated book and history
        self.repository.save_books(books)
        self.repository.save_status_history(self.status_history)

        return book

    def get_status(self, book_id: str) -> str:
        """Get the current reading status of a book.

        Args:
            book_id: ID of the book

        Returns:
            Current status

        Raises:
            ValueError: If book not found
        """
        books = self.repository.load_books()
        for book in books:
            if book.id == book_id:
                return book.status

        raise ValueError(f"Book with ID {book_id} not found")

    def get_status_history(self, book_id: str) -> List[StatusHistory]:
        """Get the status change history for a book.

        Args:
            book_id: ID of the book

        Returns:
            List of StatusHistory entries
        """
        return [h for h in self.status_history if h.book_id == book_id]

    def get_books_by_status(self, status: str) -> List[Book]:
        """Get all books with a specific reading status.

        Args:
            status: Reading status to filter by

        Returns:
            List of books with the specified status
        """
        books = self.repository.load_books()
        return [b for b in books if b.status == status]
