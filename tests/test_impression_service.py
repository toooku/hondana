"""Property-based tests for ImpressionService."""

from hypothesis import given, strategies as st
import tempfile
from src.impression_service import ImpressionService
from src.repository import DataRepository
from src.models import Impression


# Strategy for generating valid UUIDs
uuid_strategy = st.uuids().map(str)

# Strategy for generating Impression instances
impression_strategy = st.builds(
    Impression,
    book_id=uuid_strategy,
    content=st.text(min_size=1, max_size=1000),
)


class TestImpressionServiceProperties:
    """Property-based tests for ImpressionService."""

    @given(uuid_strategy, st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    def test_impression_post_and_retrieval_consistency(self, book_id: str, content: str):
        """
        **Feature: book-library, Property 6: 感想の投稿と取得の一貫性**

        For any book and impression content, when an impression is posted
        and then retrieved, the posted content should be preserved.

        **Validates: Requirements 4.1**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create impression
            created = service.create_impression(book_id, content)

            # Retrieve impression
            retrieved = service.get_impression(created.id)

            # Verify content is preserved
            assert retrieved is not None
            assert retrieved.content == content
            assert retrieved.book_id == book_id

    @given(uuid_strategy, st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    def test_impression_has_creation_timestamp(self, book_id: str, content: str):
        """
        **Feature: book-library, Property 7: 感想に投稿日時が記録される**

        For any impression, when it is posted, the creation timestamp
        should be automatically recorded.

        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create impression
            created = service.create_impression(book_id, content)

            # Verify created_at is set and is not empty
            assert created.created_at is not None
            assert len(created.created_at) > 0
            # Verify it's in ISO 8601 format (contains 'T' and 'Z')
            assert 'T' in created.created_at
            assert 'Z' in created.created_at

    @given(uuid_strategy, st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()), st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    def test_impression_update_is_reflected(self, book_id: str, original_content: str, new_content: str):
        """
        **Feature: book-library, Property 8: 感想の更新が反映される**

        For any impression and new content, when the impression is updated,
        retrieving it should show the new content.

        **Validates: Requirements 4.3**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create impression
            created = service.create_impression(book_id, original_content)

            # Update impression
            updated = service.update_impression(created.id, new_content)

            # Retrieve and verify
            retrieved = service.get_impression(created.id)
            assert retrieved is not None
            assert retrieved.content == new_content
            assert updated.content == new_content

    @given(uuid_strategy, st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    def test_impression_deletion_is_reflected(self, book_id: str, content: str):
        """
        **Feature: book-library, Property 9: 感想の削除が反映される**

        For any impression, when it is deleted, it should no longer
        be retrievable.

        **Validates: Requirements 4.4**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = DataRepository(tmpdir)
            service = ImpressionService(repo)

            # Create impression
            created = service.create_impression(book_id, content)

            # Delete impression
            deleted = service.delete_impression(created.id)

            # Verify deletion was successful
            assert deleted is True

            # Verify it's no longer retrievable
            retrieved = service.get_impression(created.id)
            assert retrieved is None
