"""Unit tests for OpenBD API client."""

import pytest
import requests
from unittest.mock import patch, MagicMock
from src.openbd_client import OpenBDClient


class TestOpenBDClient:
    """Tests for OpenBDClient class."""
    
    def test_fetch_book_info_success(self):
        """Test successful book information retrieval."""
        mock_response = {
            "summary": {
                "title": "ノルウェイの森",
                "author": "村上春樹",
                "publisher": "新潮社",
                "content": "A novel about love and loss"
            },
            "onix": {
                "ProductPublicationDetail": {
                    "PublicationDate": "19870904"
                }
            }
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [mock_response]
            mock_get.return_value.raise_for_status.return_value = None
            
            result = OpenBDClient.fetch_book_info("978-4-06-520808-7")
            
            assert result["title"] == "ノルウェイの森"
            assert result["author"] == "村上春樹"
            assert result["publisher"] == "新潮社"
            assert result["publication_date"] == "1987-09-04"
            assert result["description"] == "A novel about love and loss"
    
    def test_fetch_book_info_isbn_not_found(self):
        """Test ISBN not found error."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = []
            mock_get.return_value.raise_for_status.return_value = None
            
            with pytest.raises(OpenBDClient.ISBNNotFoundError):
                OpenBDClient.fetch_book_info("invalid-isbn")
    
    def test_fetch_book_info_network_timeout(self):
        """Test network timeout with retry logic."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            with pytest.raises(OpenBDClient.NetworkError):
                OpenBDClient.fetch_book_info("978-4-06-520808-7")
            
            # Verify retries occurred
            assert mock_get.call_count == OpenBDClient.MAX_RETRIES
    
    def test_fetch_book_info_connection_error(self):
        """Test connection error with retry logic."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            
            with pytest.raises(OpenBDClient.NetworkError):
                OpenBDClient.fetch_book_info("978-4-06-520808-7")
            
            # Verify retries occurred
            assert mock_get.call_count == OpenBDClient.MAX_RETRIES
    
    def test_fetch_book_info_with_author_list(self):
        """Test handling of author as list."""
        mock_response = {
            "summary": {
                "title": "Test Book",
                "author": ["Author One", "Author Two"],
                "publisher": "Test Publisher",
                "content": "Test description"
            },
            "onix": {
                "ProductPublicationDetail": {
                    "PublicationDate": "20240101"
                }
            }
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [mock_response]
            mock_get.return_value.raise_for_status.return_value = None
            
            result = OpenBDClient.fetch_book_info("test-isbn")
            
            assert result["author"] == "Author One, Author Two"
    
    def test_fetch_book_info_missing_publication_date(self):
        """Test handling of missing publication date."""
        mock_response = {
            "summary": {
                "title": "Test Book",
                "author": "Test Author",
                "publisher": "Test Publisher",
                "content": "Test description"
            },
            "onix": {}
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.json.return_value = [mock_response]
            mock_get.return_value.raise_for_status.return_value = None
            
            result = OpenBDClient.fetch_book_info("test-isbn")
            
            assert result["publication_date"] == ""
    
    def test_fetch_book_info_request_exception(self):
        """Test general request exception."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("General error")
            
            with pytest.raises(OpenBDClient.NetworkError):
                OpenBDClient.fetch_book_info("978-4-06-520808-7")
