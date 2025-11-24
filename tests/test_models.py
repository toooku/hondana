"""Property-based tests for data models."""

import tempfile
from hypothesis import given, strategies as st
from src.models import Book, Impression
from src.repository import DataRepository


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


@given(book_strategy)
def test_book_registration_and_retrieval_consistency(book: Book):
    """
    **Feature: book-library, Property 1: 本の登録と取得の一貫性**
    
    For any book, when it is registered and then retrieved, all information
    from registration should be preserved.
    
    **Validates: Requirements 1.2**
    """
    # Register the book by converting to dict and back
    book_dict = book.to_dict()
    retrieved_book = Book.from_dict(book_dict)
    
    # Verify all fields are preserved
    assert retrieved_book.id == book.id
    assert retrieved_book.isbn == book.isbn
    assert retrieved_book.title == book.title
    assert retrieved_book.author == book.author
    assert retrieved_book.publisher == book.publisher
    assert retrieved_book.publication_date == book.publication_date
    assert retrieved_book.description == book.description
    assert retrieved_book.created_at == book.created_at
    assert retrieved_book.updated_at == book.updated_at


# Strategy for generating Impression instances
impression_strategy = st.builds(
    Impression,
    book_id=st.uuids().map(str),
    content=st.text(min_size=1, max_size=1000),
)


@given(
    st.lists(book_strategy, min_size=1, max_size=10),
    st.lists(impression_strategy, min_size=1, max_size=10)
)
def test_data_persistence_and_restoration_consistency(
    books, impressions
):
    """
    **Feature: book-library, Property 12: データの永続化と復元の一貫性**
    
    For any books and impressions, when data is saved and then reloaded,
    the same state should be restored. This is a round-trip property.
    
    **Validates: Requirements 6.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = DataRepository(tmpdir)
        
        # Save books and impressions
        repo.save_books(books)
        repo.save_impressions(impressions)
        
        # Load books and impressions
        loaded_books = repo.load_books()
        loaded_impressions = repo.load_impressions()
        
        # Verify books are restored correctly
        assert len(loaded_books) == len(books)
        for original, loaded in zip(books, loaded_books):
            assert loaded.id == original.id
            assert loaded.isbn == original.isbn
            assert loaded.title == original.title
            assert loaded.author == original.author
            assert loaded.publisher == original.publisher
            assert loaded.publication_date == original.publication_date
            assert loaded.description == original.description
            assert loaded.created_at == original.created_at
            assert loaded.updated_at == original.updated_at
        
        # Verify impressions are restored correctly
        assert len(loaded_impressions) == len(impressions)
        for original, loaded in zip(impressions, loaded_impressions):
            assert loaded.id == original.id
            assert loaded.book_id == original.book_id
            assert loaded.content == original.content
            assert loaded.created_at == original.created_at
            assert loaded.updated_at == original.updated_at
