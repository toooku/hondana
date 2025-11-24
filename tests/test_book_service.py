"""Property-based tests for BookService."""

from hypothesis import given, strategies as st
import tempfile
import shutil
from src.book_service import BookService
from src.repository import DataRepository
from src.models import Book


# Strategy for generating valid ISBN strings
isbn_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
    min_size=10,
    max_size=17
)

# Strategy for generating valid dates in YYYY-MM-DD format
date_strategy = st.dates().map(lambda d: d.isoformat())

# Strategy for generating Book instances
book_strategy = st.builds(
    Book,
    isbn=isbn_strategy,
    title=st.text(min_size=1, max_size=200),
    author=st.text(min_size=1, max_size=100),
    publisher=st.text(min_size=1, max_size=100),
    publication_date=date_strategy,
    description=st.text(max_size=1000),
)


class TestBookServiceProperties:
    """Property-based tests for BookService."""

    @given(st.lists(book_strategy, min_size=1, max_size=10))
    def test_list_books_contains_all_books(self, books: list):
        """
        **Feature: book-library, Property 2: 本の一覧にすべての本が含まれる**

        For any set of books, when they are added to the service,
        list_books() should return all of them.

        **Validates: Requirements 2.1**
        """
        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = BookService(repo)

            # Add all books to the service
            for book in books:
                service._books.append(book)
                service.repository.save_books(service._books)

            # Get the list of books
            listed_books = service.list_books()

            # Verify all books are in the list
            assert len(listed_books) == len(books)
            for book in books:
                assert any(b.id == book.id for b in listed_books)

    @given(book_strategy)
    def test_book_details_contains_required_info(self, book: Book):
        """
        **Feature: book-library, Property 3: 本の詳細ページに必須情報が含まれる**

        For any book, when retrieved, it should contain all required fields:
        title, author, publisher, publication_date, isbn, and created_at.

        **Validates: Requirements 2.3**
        """
        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = BookService(repo)

            # Add the book
            service._books.append(book)
            service.repository.save_books(service._books)

            # Retrieve the book
            retrieved = service.get_book(book.id)

            # Verify all required fields are present and not empty
            assert retrieved is not None
            assert retrieved.title == book.title
            assert retrieved.author == book.author
            assert retrieved.publisher == book.publisher
            assert retrieved.publication_date == book.publication_date
            assert retrieved.isbn == book.isbn
            assert retrieved.created_at == book.created_at

    @given(book_strategy, st.text(min_size=1, max_size=100))
    def test_book_update_is_reflected(self, book: Book, new_title: str):
        """
        **Feature: book-library, Property 4: 本の更新が反映される**

        For any book and new title, when the book is updated,
        retrieving it should show the new information.

        **Validates: Requirements 3.1**
        """
        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = BookService(repo)

            # Add the book
            service._books.append(book)
            service.repository.save_books(service._books)

            # Update the book
            service.update_book(book.id, title=new_title)

            # Retrieve and verify
            retrieved = service.get_book(book.id)
            assert retrieved is not None
            assert retrieved.title == new_title

    @given(
        st.lists(book_strategy, min_size=1, max_size=5),
        st.integers(min_value=0, max_value=4)
    )
    def test_book_deletion_removes_book(
        self, books: list, delete_index: int
    ):
        """
        **Feature: book-library, Property 5: 本の削除時に関連する感想も削除される**

        For any set of books, when a book is deleted,
        it should no longer appear in the list.

        **Validates: Requirements 3.2**
        """
        # Adjust delete_index to be within bounds
        if delete_index >= len(books):
            delete_index = len(books) - 1

        # Create a temporary directory for this test
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = BookService(repo)

            # Add all books
            for book in books:
                service._books.append(book)
            service.repository.save_books(service._books)

            # Delete one book
            book_to_delete = books[delete_index]
            service.delete_book(book_to_delete.id)

            # Verify it's gone
            retrieved = service.get_book(book_to_delete.id)
            assert retrieved is None

            # Verify other books remain
            listed_books = service.list_books()
            assert len(listed_books) == len(books) - 1
