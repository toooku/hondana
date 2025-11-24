"""Service for managing books."""

from datetime import datetime, timezone
from typing import List, Optional

from src.markdown_impression_service import MarkdownImpressionService
from src.models import Book
from src.openbd_client import OpenBDClient
from src.repository import DataRepository


class BookService:
    """Service for managing book operations."""

    class ISBNAlreadyExistsError(Exception):
        """Raised when trying to create a book with an ISBN that already exists."""

        pass

    def __init__(
        self,
        repository: Optional[DataRepository] = None,
        markdown_impression_service: Optional[MarkdownImpressionService] = None,
    ):
        """Initialize the service with a repository."""
        self.repository = repository or DataRepository()
        self.markdown_impression_service = (
            markdown_impression_service or MarkdownImpressionService()
        )
        self._books = self.repository.load_books()

    def create_book(self, isbn: str) -> Book:
        """
        Create a new book by fetching information from OpenBD API.

        Args:
            isbn: The ISBN of the book to create

        Returns:
            The created Book instance

        Raises:
            ISBNAlreadyExistsError: If ISBN already exists in the library
            OpenBDClient.ISBNNotFoundError: If ISBN is not found
            OpenBDClient.NetworkError: If network error occurs
        """
        # Normalize ISBN (remove hyphens for comparison)
        normalized_isbn = isbn.replace("-", "")

        # Check if ISBN already exists
        existing_books = self.repository.load_books()
        for book in existing_books:
            existing_normalized_isbn = book.isbn.replace("-", "")
            if existing_normalized_isbn == normalized_isbn:
                raise self.ISBNAlreadyExistsError(
                    f"Book with ISBN {isbn} already exists in the library"
                )

        # Fetch book info from OpenBD API
        book_info = OpenBDClient.fetch_book_info(isbn)

        # Create Book instance
        book = Book(
            isbn=normalized_isbn,  # Use normalized ISBN
            title=book_info["title"],
            author=book_info["author"],
            publisher=book_info["publisher"],
            publication_date=book_info["publication_date"],
            description=book_info["description"],
            cover_url=book_info.get("cover_url", ""),  # v2: Add cover URL
            status="積読",  # v2: Default status
        )

        # Add to in-memory list
        self._books.append(book)

        # Persist to file
        self.repository.save_books(self._books)

        # Create initial Markdown impression template
        self._create_initial_markdown_impression(book)

        return book

    def _create_initial_markdown_impression(self, book: Book) -> None:
        """Create initial empty Markdown impression file for a new book.

        Args:
            book: The newly created Book instance
        """
        # Check if impression already exists
        if self.markdown_impression_service.impression_exists(book.id, book.title):
            return  # Don't overwrite existing impressions

        # Create initial empty Markdown file
        # Include book info in the filename for identification
        content = ""

        # Create the impression
        self.markdown_impression_service.create_impression(book.id, content, book.title)

    def get_book(self, book_id: str) -> Optional[Book]:
        """
        Get a book by ID.

        Args:
            book_id: The ID of the book to retrieve

        Returns:
            The Book instance or None if not found
        """
        for book in self._books:
            if book.id == book_id:
                return book
        return None

    def list_books(self) -> List[Book]:
        """
        Get all books.

        Returns:
            List of all Book instances
        """
        return self._books.copy()

    def update_book(self, book_id: str, **kwargs) -> Optional[Book]:
        """
        Update a book's information.

        Args:
            book_id: The ID of the book to update
            **kwargs: Fields to update (title, author, publisher, etc.)

        Returns:
            The updated Book instance or None if not found
        """
        book = self.get_book(book_id)
        if not book:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(book, key) and key not in ["id", "created_at"]:
                setattr(book, key, value)

        # Update the updated_at timestamp
        book.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Persist to file
        self.repository.save_books(self._books)

        return book

    def delete_book(self, book_id: str) -> bool:
        """
        Delete a book by ID.

        Args:
            book_id: The ID of the book to delete

        Returns:
            True if book was deleted, False if not found
        """
        book = self.get_book(book_id)
        if not book:
            return False

        self._books = [b for b in self._books if b.id != book_id]

        # Persist to file
        self.repository.save_books(self._books)

        return True

    def fetch_missing_cover_urls(self) -> None:
        """
        Fetch cover URLs for books that don't have them from OpenBD API.
        This is useful for updating existing books with cover images.
        """
        updated = False
        for book in self._books:
            if not book.cover_url and book.isbn:
                try:
                    book_info = OpenBDClient.fetch_book_info(book.isbn)
                    cover_url = book_info.get("cover_url", "")
                    if cover_url:
                        book.cover_url = cover_url
                        book.updated_at = (
                            datetime.now(timezone.utc)
                            .isoformat()
                            .replace("+00:00", "Z")
                        )
                        updated = True
                except (OpenBDClient.ISBNNotFoundError, OpenBDClient.NetworkError):
                    # Skip if we can't fetch the cover
                    pass

        if updated:
            self.repository.save_books(self._books)
