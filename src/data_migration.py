"""Data migration utilities for v1 to v2 upgrade."""

import json
import os
from typing import Any, Dict, List

from src.markdown_impression_service import MarkdownImpressionService
from src.models import Book, Impression


class DataMigration:
    """Utility for migrating data from v1 to v2."""

    @staticmethod
    def migrate_books_v1_to_v2(
        v1_books_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Migrate v1 book data to v2 format.

        Args:
            v1_books_data: List of v1 book dictionaries

        Returns:
            List of v2 book dictionaries with new fields
        """
        v2_books = []

        for book_data in v1_books_data:
            v2_book = book_data.copy()

            # Add v2 fields with defaults
            if "cover_url" not in v2_book:
                v2_book["cover_url"] = ""
            if "status" not in v2_book:
                v2_book["status"] = "積読"

            v2_books.append(v2_book)

        return v2_books

    @staticmethod
    def migrate_impressions_to_markdown(
        v1_impressions_data: List[Dict[str, Any]],
        markdown_impression_service: MarkdownImpressionService,
    ) -> None:
        """Migrate v1 impression data to Markdown files.

        Args:
            v1_impressions_data: List of v1 impression dictionaries
            markdown_impression_service: MarkdownImpressionService instance
        """
        for impression_data in v1_impressions_data:
            book_id = impression_data.get("book_id")
            content = impression_data.get("content", "")

            if book_id and content:
                try:
                    markdown_impression_service.create_impression(book_id, content)
                except (ValueError, IOError):
                    # Skip if creation fails
                    pass

    @staticmethod
    def migrate_from_v1(
        v1_books_file: str = "data/books.json",
        v1_impressions_file: str = "data/impressions.json",
    ) -> bool:
        """Perform full migration from v1 to v2.

        Args:
            v1_books_file: Path to v1 books.json
            v1_impressions_file: Path to v1 impressions.json

        Returns:
            True if migration successful, False otherwise
        """
        try:
            # Read v1 data
            v1_books = []
            v1_impressions = []

            if os.path.exists(v1_books_file):
                with open(v1_books_file, "r", encoding="utf-8") as f:
                    v1_books = json.load(f)

            if os.path.exists(v1_impressions_file):
                with open(v1_impressions_file, "r", encoding="utf-8") as f:
                    v1_impressions = json.load(f)

            # Migrate books
            v2_books = DataMigration.migrate_books_v1_to_v2(v1_books)

            # Write migrated books back
            with open(v1_books_file, "w", encoding="utf-8") as f:
                json.dump(v2_books, f, ensure_ascii=False, indent=2)

            # Migrate impressions to Markdown
            markdown_service = MarkdownImpressionService()
            DataMigration.migrate_impressions_to_markdown(
                v1_impressions, markdown_service
            )

            return True
        except Exception:
            return False
