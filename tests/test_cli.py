"""Unit tests for CLI commands."""

import tempfile
import shutil
import os
from click.testing import CliRunner
from src.cli import cli
from src.repository import DataRepository
from src.book_service import BookService
from src.impression_service import ImpressionService
from src.models import Book, Impression


class TestCLIBookCommands:
    """Tests for book management CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_list_books_empty(self):
        """Test listing books when none exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["list-books"])
            assert result.exit_code == 0
            assert "登録されている本がありません" in result.output

    def test_list_books_with_books(self):
        """Test listing books when books exist."""
        with self.runner.isolated_filesystem():
            # Create test data in isolated filesystem
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(cli, ["list-books"])
            assert result.exit_code == 0
            assert "ノルウェイの森" in result.output
            assert "村上春樹" in result.output

    def test_show_book_not_found(self):
        """Test showing a book that doesn't exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["show-book", "nonexistent-id"])
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_show_book_found(self):
        """Test showing a book that exists."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(cli, ["show-book", book.id])
            assert result.exit_code == 0
            assert "ノルウェイの森" in result.output
            assert "村上春樹" in result.output

    def test_update_book_not_found(self):
        """Test updating a book that doesn't exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["update-book", "nonexistent-id", "--title", "新しいタイトル"]
            )
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_update_book_no_options(self):
        """Test updating a book without specifying any fields."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(cli, ["update-book", book.id])
            assert result.exit_code == 1
            assert "更新する項目を指定してください" in result.output

    def test_delete_book_not_found(self):
        """Test deleting a book that doesn't exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["delete-book", "nonexistent-id", "--confirm"]
            )
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_delete_book_with_confirm(self):
        """Test deleting a book with confirmation flag."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(
                cli,
                ["delete-book", book.id, "--confirm"]
            )
            assert result.exit_code == 0
            assert "削除しました" in result.output


class TestCLIImpressionCommands:
    """Tests for impression management CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_add_impression_book_not_found(self):
        """Test adding an impression to a non-existent book."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["add-impression", "nonexistent-id", "素晴らしい本です"]
            )
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_add_impression_empty_content(self):
        """Test adding an impression with empty content."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(
                cli,
                ["add-impression", book.id, ""]
            )
            assert result.exit_code == 1
            assert "Impression content cannot be empty" in result.output

    def test_add_impression_success(self):
        """Test successfully adding an impression."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(
                cli,
                ["add-impression", book.id, "素晴らしい本です"]
            )
            assert result.exit_code == 0
            assert "投稿しました" in result.output

    def test_update_impression_not_found(self):
        """Test updating an impression that doesn't exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["update-impression", "nonexistent-id", "新しい内容"]
            )
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_update_impression_empty_content(self):
        """Test updating an impression with empty content."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            impression_service = ImpressionService(repo)

            impression = Impression(
                book_id="book-id",
                content="元の内容",
            )
            impression_service._impressions.append(impression)
            impression_service.repository.save_impressions(impression_service._impressions)

            result = self.runner.invoke(
                cli,
                ["update-impression", impression.id, ""]
            )
            assert result.exit_code == 1
            assert "Impression content cannot be empty" in result.output

    def test_delete_impression_not_found(self):
        """Test deleting an impression that doesn't exist."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["delete-impression", "nonexistent-id", "--confirm"]
            )
            assert result.exit_code == 1
            assert "見つかりません" in result.output

    def test_delete_impression_with_confirm(self):
        """Test deleting an impression with confirmation flag."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            book_service = BookService(repo)
            impression_service = ImpressionService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            book_service._books.append(book)
            book_service.repository.save_books(book_service._books)

            impression = Impression(
                book_id=book.id,
                content="素晴らしい本です",
            )
            impression_service._impressions.append(impression)
            impression_service.repository.save_impressions(impression_service._impressions)

            result = self.runner.invoke(
                cli,
                ["delete-impression", impression.id, "--confirm"]
            )
            assert result.exit_code == 0
            assert "削除しました" in result.output


class TestCLISiteGenerationCommands:
    """Tests for static site generation CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_generate_site_empty(self):
        """Test generating site with no books."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["generate-site"])
            assert result.exit_code == 0
            assert "生成しました" in result.output

    def test_generate_site_with_books(self):
        """Test generating site with books."""
        with self.runner.isolated_filesystem():
            # Create test data
            repo = DataRepository("data")
            service = BookService(repo)

            book = Book(
                isbn="978-4-06-520808-7",
                title="ノルウェイの森",
                author="村上春樹",
                publisher="新潮社",
                publication_date="1987-09-04",
                description="素晴らしい作品",
            )
            service._books.append(book)
            service.repository.save_books(service._books)

            result = self.runner.invoke(cli, ["generate-site"])
            assert result.exit_code == 0
            assert "生成しました" in result.output

    def test_generate_site_custom_output(self):
        """Test generating site with custom output directory."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                cli,
                ["generate-site", "--output", "custom_output"]
            )
            assert result.exit_code == 0
            assert "custom_output" in result.output
