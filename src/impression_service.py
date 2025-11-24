"""Service for managing impressions (reviews/comments)."""

from datetime import datetime, timezone
from typing import List, Optional

from src.models import Impression
from src.repository import DataRepository


class ImpressionService:
    """Service for managing impression operations."""

    def __init__(self, repository: Optional[DataRepository] = None):
        """Initialize the service with a repository."""
        self.repository = repository or DataRepository()
        self._impressions = self.repository.load_impressions()

    def create_impression(self, book_id: str, content: str) -> Impression:
        """
        Create a new impression for a book.

        Args:
            book_id: The ID of the book
            content: The impression content

        Returns:
            The created Impression instance

        Raises:
            ValueError: If content is empty or only whitespace
        """
        # Validate input
        if not content or not content.strip():
            raise ValueError("Impression content cannot be empty")

        impression = Impression(
            book_id=book_id,
            content=content,
        )

        # Add to in-memory list
        self._impressions.append(impression)

        # Persist to file
        self.repository.save_impressions(self._impressions)

        return impression

    def get_impression(self, impression_id: str) -> Optional[Impression]:
        """
        Get an impression by ID.

        Args:
            impression_id: The ID of the impression to retrieve

        Returns:
            The Impression instance or None if not found
        """
        for impression in self._impressions:
            if impression.id == impression_id:
                return impression
        return None

    def list_impressions_by_book(self, book_id: str) -> List[Impression]:
        """
        Get all impressions for a specific book.

        Args:
            book_id: The ID of the book

        Returns:
            List of Impression instances for the book
        """
        return [imp for imp in self._impressions if imp.book_id == book_id]

    def update_impression(
        self, impression_id: str, content: str
    ) -> Optional[Impression]:
        """
        Update an impression's content.

        Args:
            impression_id: The ID of the impression to update
            content: The new content

        Returns:
            The updated Impression instance or None if not found

        Raises:
            ValueError: If content is empty or only whitespace
        """
        # Validate input
        if not content or not content.strip():
            raise ValueError("Impression content cannot be empty")

        impression = self.get_impression(impression_id)
        if not impression:
            return None

        # Update content
        impression.content = content

        # Update the updated_at timestamp
        impression.updated_at = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Persist to file
        self.repository.save_impressions(self._impressions)

        return impression

    def delete_impression(self, impression_id: str) -> bool:
        """
        Delete an impression by ID.

        Args:
            impression_id: The ID of the impression to delete

        Returns:
            True if impression was deleted, False if not found
        """
        impression = self.get_impression(impression_id)
        if not impression:
            return False

        self._impressions = [
            imp for imp in self._impressions if imp.id != impression_id
        ]

        # Persist to file
        self.repository.save_impressions(self._impressions)

        return True

    def delete_impressions_by_book(self, book_id: str) -> int:
        """
        Delete all impressions for a specific book.

        Args:
            book_id: The ID of the book

        Returns:
            The number of impressions deleted
        """
        initial_count = len(self._impressions)
        self._impressions = [imp for imp in self._impressions if imp.book_id != book_id]
        deleted_count = initial_count - len(self._impressions)

        # Persist to file
        self.repository.save_impressions(self._impressions)

        return deleted_count
