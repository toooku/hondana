"""Property-based tests for StaticSiteGenerator."""

from hypothesis import given, strategies as st
import tempfile
import os
from src.static_site_generator import StaticSiteGenerator
from src.book_service import BookService
from src.impression_service import ImpressionService
from src.repository import DataRepository
from src.models import Book, Impression


# Strategy for generating valid ISBN strings
isbn_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cc", "Cs"),
        blacklist_characters="\r\n\t"
    ),
    min_size=10,
    max_size=17
)

# Strategy for generating valid dates in YYYY-MM-DD format
date_strategy = st.dates().map(lambda d: d.isoformat())

# Strategy for generating Book instances
book_strategy = st.builds(
    Book,
    isbn=isbn_strategy,
    title=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters="\r\n\t"
        ),
        min_size=1,
        max_size=200
    ),
    author=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters="\r\n\t"
        ),
        min_size=1,
        max_size=100
    ),
    publisher=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters="\r\n\t"
        ),
        min_size=1,
        max_size=100
    ),
    publication_date=date_strategy,
    description=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters="\r\n\t"
        ),
        max_size=1000
    ),
)

# Strategy for generating Impression instances
impression_strategy = st.builds(
    Impression,
    book_id=st.uuids().map(str),
    content=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cc", "Cs"),
            blacklist_characters="\r\n\t"
        ),
        min_size=1,
        max_size=500
    ),
)


class TestStaticSiteGeneratorProperties:
    """Property-based tests for StaticSiteGenerator."""

    @given(st.lists(book_strategy, min_size=1, max_size=10))
    def test_all_books_included_in_html(self, books: list):
        """
        **Feature: book-library, Property 10: 静的サイト生成ですべての本がHTMLに含まれる**

        For any set of books, when the static site is generated,
        all books should be included in the generated HTML files.

        **Validates: Requirements 5.1**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create services with temporary data directory
            data_dir = os.path.join(tmpdir, "data")
            repo = DataRepository(data_dir)
            book_service = BookService(repo)
            impression_service = ImpressionService(repo)

            # Add all books to the service
            for book in books:
                book_service._books.append(book)
            book_service.repository.save_books(book_service._books)

            # Generate the static site
            output_dir = os.path.join(tmpdir, "output")
            generator = StaticSiteGenerator(
                book_service,
                impression_service,
                output_dir
            )
            generator.generate()

            # Read the index.html file
            index_path = os.path.join(output_dir, "index.html")
            assert os.path.exists(index_path), "index.html should be generated"

            with open(index_path, "r", encoding="utf-8") as f:
                index_content = f.read()

            # Verify all books are in the index
            for book in books:
                # Check for escaped HTML version of title
                escaped_title = StaticSiteGenerator._escape_html(book.title)
                assert escaped_title in index_content, \
                    f"Book title '{escaped_title}' should be in index.html"
                assert f"books/{book.id}.html" in index_content, \
                    f"Book link for '{book.id}' should be in index.html"

            # Verify all book detail pages exist
            for book in books:
                book_page_path = os.path.join(
                    output_dir,
                    "books",
                    f"{book.id}.html"
                )
                assert os.path.exists(book_page_path), \
                    f"Book detail page for '{book.id}' should exist"

    @given(
        st.lists(book_strategy, min_size=1, max_size=5),
        st.lists(impression_strategy, min_size=0, max_size=10)
    )
    def test_book_details_in_html(self, books: list, impressions: list):
        """
        **Feature: book-library, Property 11: 生成されたHTMLに本の詳細情報が含まれる**

        For any book and its impressions, when the detail page is generated,
        all book information and related impressions should be included.

        **Validates: Requirements 5.3**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create services with temporary data directory
            data_dir = os.path.join(tmpdir, "data")
            repo = DataRepository(data_dir)
            book_service = BookService(repo)
            impression_service = ImpressionService(repo)

            # Add books
            for book in books:
                book_service._books.append(book)
            book_service.repository.save_books(book_service._books)

            # Add impressions for the first book if available
            if books and impressions:
                first_book_id = books[0].id
                for impression in impressions:
                    impression.book_id = first_book_id
                    impression_service._impressions.append(impression)
                impression_service.repository.save_impressions(
                    impression_service._impressions
                )

            # Generate the static site
            output_dir = os.path.join(tmpdir, "output")
            generator = StaticSiteGenerator(
                book_service,
                impression_service,
                output_dir
            )
            generator.generate()

            # Check each book's detail page
            for book in books:
                book_page_path = os.path.join(
                    output_dir,
                    "books",
                    f"{book.id}.html"
                )
                assert os.path.exists(book_page_path)

                with open(book_page_path, "r", encoding="utf-8") as f:
                    page_content = f.read()

                # Verify required book information is present
                # (using escaped HTML versions)
                escaped_title = StaticSiteGenerator._escape_html(book.title)
                escaped_author = StaticSiteGenerator._escape_html(book.author)
                escaped_publisher = StaticSiteGenerator._escape_html(
                    book.publisher
                )
                escaped_isbn = StaticSiteGenerator._escape_html(book.isbn)

                assert escaped_title in page_content, \
                    f"Book title should be in detail page"
                assert escaped_author in page_content, \
                    f"Book author should be in detail page"
                assert escaped_publisher in page_content, \
                    f"Book publisher should be in detail page"
                assert book.publication_date in page_content, \
                    f"Book publication_date should be in detail page"
                assert escaped_isbn in page_content, \
                    f"Book ISBN should be in detail page"
                assert book.created_at in page_content, \
                    f"Book created_at should be in detail page"

                # If this is the first book and has impressions,
                # verify they are included
                if book.id == books[0].id and impressions:
                    for impression in impressions:
                        escaped_content = (
                            StaticSiteGenerator._escape_html(
                                impression.content
                            )
                        )
                        assert escaped_content in page_content, \
                            f"Impression content should be in detail page"
