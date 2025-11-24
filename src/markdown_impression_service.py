"""Service for managing impressions as Markdown files."""

import os
from datetime import datetime, timezone
from typing import Optional

from src.models import Impression


class MarkdownImpressionService:
    """Service for managing book impressions as Markdown files."""

    def __init__(self, impressions_dir: str = "data/impressions"):
        """Initialize the Markdown impression service.

        Args:
            impressions_dir: Directory to store impression Markdown files
        """
        self.impressions_dir = impressions_dir
        os.makedirs(impressions_dir, exist_ok=True)

    def _get_impression_file_path(self, book_id: str, book_title: str = "") -> str:
        """Get the file path for a book's impression file."""
        if book_title:
            safe_title = self._sanitize_filename(book_title)
            return os.path.join(self.impressions_dir, f"{safe_title}_{book_id}.md")
        else:
            return os.path.join(self.impressions_dir, f"{book_id}.md")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing invalid characters and limiting length."""
        import re

        # Remove or replace invalid characters
        # Windows: < > : " | ? * \ /
        # Unix: / (null byte is already handled)
        invalid_chars = r'[<>:"|?*\\/]'
        safe_name = re.sub(invalid_chars, "_", filename)

        # Remove control characters
        safe_name = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", safe_name)

        # Limit length (considering the ID part, keep reasonable length)
        max_title_length = 50
        if len(safe_name) > max_title_length:
            safe_name = safe_name[:max_title_length].rstrip("_")

        # Ensure it's not empty
        if not safe_name.strip():
            safe_name = "untitled"

        return safe_name

    def create_impression(
        self, book_id: str, content: str, book_title: str = ""
    ) -> Impression:
        """Create a new impression for a book.

        Args:
            book_id: ID of the book
            content: Markdown content of the impression

        Returns:
            Impression instance

        Raises:
            ValueError: If content is empty or whitespace only
        """
        # Allow empty content for initial file creation
        # if not content or not content.strip():
        #     raise ValueError("Impression content cannot be empty")

        file_path = self._get_impression_file_path(book_id, book_title)

        # Write Markdown file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Create Impression instance
        impression = Impression(book_id=book_id, content=content)

        return impression

    def get_impression(self, book_id: str, book_title: str = "") -> Optional[str]:
        """Get the impression content for a book.

        Args:
            book_id: ID of the book
            book_title: Title of the book (for filename lookup)

        Returns:
            Markdown content of the impression, or None if not found
        """
        # Try new format first (with title), then fallback to old format
        file_path_with_title = self._get_impression_file_path(book_id, book_title)
        file_path_old = self._get_impression_file_path(book_id)

        # Check new format first
        if book_title and os.path.exists(file_path_with_title):
            file_path = file_path_with_title
        elif os.path.exists(file_path_old):
            file_path = file_path_old
        else:
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except IOError:
            return None

    def update_impression(self, book_id: str, content: str) -> Impression:
        """Update an existing impression for a book.

        Args:
            book_id: ID of the book
            content: New Markdown content

        Returns:
            Updated Impression instance

        Raises:
            ValueError: If content is empty or whitespace only
        """
        if not content or not content.strip():
            raise ValueError("Impression content cannot be empty")

        file_path = self._get_impression_file_path(book_id)

        # Write updated Markdown file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Create updated Impression instance
        impression = Impression(book_id=book_id, content=content)

        return impression

    def delete_impression(self, book_id: str) -> bool:
        """Delete an impression for a book.

        Args:
            book_id: ID of the book

        Returns:
            True if deleted, False if file didn't exist
        """
        file_path = self._get_impression_file_path(book_id)

        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)
            return True
        except IOError:
            return False

    def impression_exists(self, book_id: str, book_title: str = "") -> bool:
        """Check if an impression exists for a book.

        Args:
            book_id: ID of the book
            book_title: Title of the book (for filename lookup)

        Returns:
            True if impression file exists
        """
        # Check both new format and old format
        file_path_with_title = self._get_impression_file_path(book_id, book_title)
        file_path_old = self._get_impression_file_path(book_id)

        return (book_title and os.path.exists(file_path_with_title)) or os.path.exists(
            file_path_old
        )
