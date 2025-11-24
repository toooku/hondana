"""Unit tests for error handling in the book library application."""

import pytest
import json
import tempfile
import os
from src.impression_service import ImpressionService
from src.repository import DataRepository


class TestImpressionErrorHandling:
    """Tests for error handling in impression operations."""

    def test_create_impression_with_empty_content(self):
        """Test that creating an impression with empty content raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            with pytest.raises(ValueError, match="Impression content cannot be empty"):
                service.create_impression("book-id", "")

    def test_create_impression_with_whitespace_only_content(self):
        """Test that creating an impression with whitespace-only content raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            with pytest.raises(ValueError, match="Impression content cannot be empty"):
                service.create_impression("book-id", "   \t\n  ")

    def test_update_impression_with_empty_content(self):
        """Test that updating an impression with empty content raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create an impression first
            impression = service.create_impression("book-id", "Original content")

            # Try to update with empty content
            with pytest.raises(ValueError, match="Impression content cannot be empty"):
                service.update_impression(impression.id, "")

    def test_update_impression_with_whitespace_only_content(self):
        """Test that updating an impression with whitespace-only content raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create an impression first
            impression = service.create_impression("book-id", "Original content")

            # Try to update with whitespace-only content
            with pytest.raises(ValueError, match="Impression content cannot be empty"):
                service.update_impression(impression.id, "   \n\t  ")


class TestRepositoryErrorHandling:
    """Tests for error handling in data repository operations."""

    def test_load_books_with_corrupted_json(self):
        """Test that loading corrupted books.json raises IOError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a corrupted JSON file
            books_file = os.path.join(tmpdir, "books.json")
            with open(books_file, "w") as f:
                f.write("{invalid json content")

            repo = DataRepository(tmpdir)

            with pytest.raises(IOError, match="Data file.*is corrupted"):
                repo.load_books()

    def test_load_impressions_with_corrupted_json(self):
        """Test that loading corrupted impressions.json raises IOError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a corrupted JSON file
            impressions_file = os.path.join(tmpdir, "impressions.json")
            with open(impressions_file, "w") as f:
                f.write("[{incomplete json")

            repo = DataRepository(tmpdir)

            with pytest.raises(IOError, match="Data file.*is corrupted"):
                repo.load_impressions()

    def test_load_books_with_valid_json_after_corruption(self):
        """Test that valid JSON can be loaded after fixing corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            books_file = os.path.join(tmpdir, "books.json")

            # First, create corrupted file
            with open(books_file, "w") as f:
                f.write("{invalid")

            repo = DataRepository(tmpdir)

            # Should raise error
            with pytest.raises(IOError):
                repo.load_books()

            # Now fix the file
            with open(books_file, "w") as f:
                json.dump([], f)

            # Should work now
            books = repo.load_books()
            assert books == []

    def test_load_impressions_with_valid_json_after_corruption(self):
        """Test that valid JSON can be loaded after fixing corruption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            impressions_file = os.path.join(tmpdir, "impressions.json")

            # First, create corrupted file
            with open(impressions_file, "w") as f:
                f.write("[{invalid")

            repo = DataRepository(tmpdir)

            # Should raise error
            with pytest.raises(IOError):
                repo.load_impressions()

            # Now fix the file
            with open(impressions_file, "w") as f:
                json.dump([], f)

            # Should work now
            impressions = repo.load_impressions()
            assert impressions == []
