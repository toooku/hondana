"""Data models for the book library application."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Book:
    """Represents a book in the library."""

    isbn: str
    title: str
    author: str
    publisher: str
    publication_date: str  # YYYY-MM-DD format
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    cover_url: str = ""  # v2: Book cover image URL from OpenBD API
    status: str = "積読"  # v2: Reading status (積読/読書中/読了)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict:
        """Convert the Book instance to a dictionary."""
        return {
            "id": self.id,
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "publication_date": self.publication_date,
            "description": self.description,
            "cover_url": self.cover_url,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Create a Book instance from a dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            isbn=data["isbn"],
            title=data["title"],
            author=cls._clean_author_name_for_display(data["author"]),
            publisher=data["publisher"],
            publication_date=data["publication_date"],
            description=data["description"],
            cover_url=data.get("cover_url", ""),
            status=data.get("status", "積読"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
        )

    @staticmethod
    def _clean_author_name_for_display(author_name: str) -> str:
        """Clean up author name for display by removing commas and unwanted parts."""
        if not author_name:
            return ""

        # Handle cases with mixed separators (spaces and commas)
        # First, split by spaces to preserve intentional groupings
        space_parts = author_name.split()

        cleaned_parts = []
        for part in space_parts:
            # For each space-separated part, clean up comma-separated elements
            comma_parts = [subpart.strip() for subpart in part.split(",") if subpart.strip()]

            # Remove parts that look like dates or other metadata
            clean_comma_parts = []
            for subpart in comma_parts:
                # Skip parts that are just numbers or contain only numbers and hyphens/slashes
                if subpart.replace("-", "").replace("/", "").isdigit():
                    continue
                # Skip parts that are clearly metadata (like birth years)
                if len(subpart) <= 4 and subpart.replace("-", "").isdigit():
                    continue
                clean_comma_parts.append(subpart)

            # Take first 1-2 clean parts from comma-separated elements
            if clean_comma_parts:
                cleaned_parts.extend(clean_comma_parts[:2])

        return " ".join(cleaned_parts) if cleaned_parts else ""



@dataclass
class Impression:
    """Represents an impression (review/comment) about a book."""
    
    book_id: str
    content: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict:
        """Convert the Impression instance to a dictionary."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Impression":
        """Create an Impression instance from a dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            book_id=data["book_id"],
            content=data["content"],
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
        )


@dataclass
class StatusHistory:
    """Represents a reading status change history for a book."""
    
    book_id: str
    old_status: str
    new_status: str
    id: str = field(default_factory=lambda: str(uuid4()))
    changed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    
    def to_dict(self) -> dict:
        """Convert the StatusHistory instance to a dictionary."""
        return {
            "id": self.id,
            "book_id": self.book_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_at": self.changed_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StatusHistory":
        """Create a StatusHistory instance from a dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            book_id=data["book_id"],
            old_status=data["old_status"],
            new_status=data["new_status"],
            changed_at=data.get("changed_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")),
        )
