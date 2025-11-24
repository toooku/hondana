"""OpenBD API client for fetching book information."""

import requests
from typing import Dict, Any
from datetime import datetime, timezone
import time


class OpenBDClient:
    """Client for interacting with the OpenBD API."""
    
    BASE_URL = "https://api.openbd.jp/v1/get"
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    TIMEOUT = 10  # seconds
    
    class ISBNNotFoundError(Exception):
        """Raised when ISBN is not found in OpenBD API."""
        pass
    
    class NetworkError(Exception):
        """Raised when network error occurs."""
        pass
    
    @classmethod
    def fetch_book_info(cls, isbn: str) -> Dict[str, Any]:
        """
        Fetch book information from OpenBD API by ISBN.

        Args:
            isbn: The ISBN of the book to fetch

        Returns:
            Dictionary containing book information with keys:
            - title: Book title
            - author: Book author
            - publisher: Publisher name
            - publication_date: Publication date in YYYY-MM-DD format
            - description: Book description
            - cover_url: Book cover image URL (v2)

        Raises:
            ISBNNotFoundError: If ISBN is not found in OpenBD API
            NetworkError: If network error occurs after retries
        """
        for attempt in range(cls.MAX_RETRIES):
            try:
                response = requests.get(
                    cls.BASE_URL,
                    params={"isbn": isbn},
                    timeout=cls.TIMEOUT
                )
                response.raise_for_status()
                
                data = response.json()
                
                # OpenBD API returns a list with one element or empty list
                if not data or len(data) == 0:
                    raise cls.ISBNNotFoundError(f"ISBN {isbn} not found in OpenBD API")
                
                book_data = data[0]
                
                # Check if book_data is None (ISBN not found)
                if book_data is None:
                    raise cls.ISBNNotFoundError(f"ISBN {isbn} not found in OpenBD API")
                
                # Extract book information from OpenBD response
                summary = book_data.get("summary", {})

                # Get publication date from onix data
                onix = book_data.get("onix", {})
                publication_date = cls._extract_publication_date(onix)

                # Get cover URL (v2)
                cover_url = cls._extract_cover_url(book_data)

                book_info = {
                    "title": summary.get("title", ""),
                    "author": cls._extract_author(summary),
                    "publisher": summary.get("publisher", ""),
                    "publication_date": publication_date,
                    "description": summary.get("content", ""),
                    "cover_url": cover_url,
                }

                return book_info
                
            except requests.exceptions.Timeout:
                if attempt < cls.MAX_RETRIES - 1:
                    time.sleep(cls.RETRY_DELAY)
                    continue
                raise cls.NetworkError(f"Request timeout after {cls.MAX_RETRIES} attempts")
            except requests.exceptions.ConnectionError:
                if attempt < cls.MAX_RETRIES - 1:
                    time.sleep(cls.RETRY_DELAY)
                    continue
                raise cls.NetworkError(f"Connection error after {cls.MAX_RETRIES} attempts")
            except requests.exceptions.RequestException as e:
                raise cls.NetworkError(f"Request failed: {str(e)}")
    



    @staticmethod
    def _extract_author(summary: Dict[str, Any]) -> str:
        """Extract author name from summary data."""
        if not summary or not isinstance(summary, dict):
            return ""
        author = summary.get("author", "")
        if isinstance(author, list):
            author = ", ".join(author) if author else ""
        if isinstance(author, str):
            # Clean up author name by removing commas and extra information
            author = OpenBDClient._clean_author_name(author)
        return author if author else ""

    @staticmethod
    def _clean_author_name(author_name: str) -> str:
        """Clean up author name by removing commas and unwanted parts."""
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
    
    @staticmethod
    def _extract_publication_date(onix: Dict[str, Any]) -> str:
        """Extract publication date from onix data in YYYY-MM-DD format."""
        try:
            # Try to get publication date from onix
            product_publication = onix.get("ProductPublicationDetail", {})
            publication_date = product_publication.get("PublicationDate", "")
            
            if publication_date:
                # OpenBD returns dates in YYYYMMDD format
                if len(publication_date) == 8:
                    return f"{publication_date[0:4]}-{publication_date[4:6]}-{publication_date[6:8]}"
                return publication_date
            
            return ""
        except (KeyError, IndexError, AttributeError):
            return ""
    
    @staticmethod
    def _extract_cover_url(book_data: Dict[str, Any]) -> str:
        """Extract cover image URL from book data (v2).
        
        OpenBD API provides cover URLs in multiple sources.
        Priority order:
        1. summary.cover (but fix ISBN format if needed)
        2. onix.CollateralDetail.SupportingResource[].ResourceLink
        3. hanmoto data (if available)
        4. Google Books API (fallback)
        """
        try:
            if not book_data:
                return ""
            
            summary = book_data.get("summary", {})
            isbn = summary.get("isbn", "") if isinstance(summary, dict) else ""
            # Remove hyphens from ISBN for cover URL
            isbn_clean = isbn.replace("-", "") if isbn else ""
            
            # 1. Try NDL (National Diet Library) first - highest quality
            if isbn_clean:
                ndl_cover = OpenBDClient._get_ndl_cover(isbn_clean)
                if ndl_cover:
                    return ndl_cover
            
            # 2. Try summary.cover
            if isinstance(summary, dict):
                cover = summary.get("cover", "")
                if cover:
                    # Fix ISBN format in cover URL if it contains hyphens
                    # OpenBD cover URLs should use ISBN without hyphens
                    if isbn and "-" in isbn and isbn in cover:
                        cover = cover.replace(isbn, isbn_clean)
                    # Verify if the URL is accessible
                    if OpenBDClient._verify_cover_url(cover):
                        return cover
            
            # 3. Try onix SupportingResource
            onix = book_data.get("onix", {})
            if isinstance(onix, dict):
                collateral = onix.get("CollateralDetail", {})
                if isinstance(collateral, dict):
                    supporting_resources = collateral.get("SupportingResource", [])
                    if isinstance(supporting_resources, list):
                        for resource in supporting_resources:
                            if isinstance(resource, dict):
                                resource_content_type = resource.get("ResourceContentType", "")
                                if resource_content_type == "01":  # 01 = Front cover
                                    resource_versions = resource.get("ResourceVersion", [])
                                    if isinstance(resource_versions, list):
                                        for version in resource_versions:
                                            if isinstance(version, dict):
                                                resource_link = version.get("ResourceLink", "")
                                                if resource_link:
                                                    # Fix ISBN format in resource link if needed
                                                    if isbn and "-" in isbn and isbn in resource_link:
                                                        resource_link = resource_link.replace(isbn, isbn_clean)
                                                    if OpenBDClient._verify_cover_url(resource_link):
                                                        return resource_link
            
            # 4. Try hanmoto data (hanmoto may have cover image info)
            hanmoto = book_data.get("hanmoto", {})
            if isinstance(hanmoto, dict):
                # Check for any image-related fields in hanmoto
                for key, value in hanmoto.items():
                    if isinstance(value, str) and ("jpg" in value.lower() or "png" in value.lower()) and "http" in value.lower():
                        if OpenBDClient._verify_cover_url(value):
                            return value
            
            # 5. Try Rakuten Books
            if isbn_clean:
                rakuten_cover = OpenBDClient._get_rakuten_books_cover(isbn_clean)
                if rakuten_cover:
                    return rakuten_cover
            
            # 6. Try Google Books API as final fallback
            if isbn_clean:
                google_cover = OpenBDClient._get_google_books_cover(isbn_clean)
                if google_cover:
                    return google_cover
            
            return ""
        except (KeyError, AttributeError, TypeError):
            return ""
    
    @staticmethod
    def _verify_cover_url(url: str) -> bool:
        """Verify if a cover URL is accessible (returns 200 or 301/302)."""
        try:
            response = requests.head(url, timeout=2, allow_redirects=False)
            return response.status_code in [200, 301, 302]
        except Exception:
            return False
    
    @staticmethod
    def _get_google_books_cover(isbn: str) -> str:
        """Get cover image URL from Google Books API."""
        try:
            response = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": f"isbn:{isbn}"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items and len(items) > 0:
                    volume_info = items[0].get("volumeInfo", {})
                    image_links = volume_info.get("imageLinks", {})
                    # Try to get the largest available image
                    # Priority: extraLarge > large > medium > thumbnail
                    for size in ["extraLarge", "large", "medium", "thumbnail"]:
                        if size in image_links:
                            cover_url = image_links[size].replace("http://", "https://")
                            # Keep default zoom parameter as-is (don't modify)
                            return cover_url
            return ""
        except Exception:
            return ""
    
    @staticmethod
    def _get_rakuten_books_cover(isbn: str) -> str:
        """Get cover image URL from Rakuten Books (no API key required for images)."""
        try:
            # Rakuten Books provides cover images via direct URL pattern
            # Format: https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/{isbn_prefix}/{isbn}.jpg
            if len(isbn) == 13:
                # Use last 4 digits for the path
                isbn_suffix = isbn[-4:]
                # Try common Rakuten Books image URL patterns
                rakuten_url = f"https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/{isbn_suffix}/{isbn}.jpg"
                if OpenBDClient._verify_cover_url(rakuten_url):
                    return rakuten_url
                
                # Alternative pattern
                rakuten_url = f"https://thumbnail.image.rakuten.co.jp/@0_mall/book/cabinet/{isbn}.jpg"
                if OpenBDClient._verify_cover_url(rakuten_url):
                    return rakuten_url
            
            return ""
        except Exception:
            return ""
    
    @staticmethod
    def _get_ndl_cover(isbn: str) -> str:
        """Get cover image URL from NDL (National Diet Library)."""
        try:
            # NDL provides cover images via direct URL
            # Format: https://iss.ndl.go.jp/thumbnail/{isbn}
            if isbn:
                ndl_url = f"https://iss.ndl.go.jp/thumbnail/{isbn}"
                # Quick check with short timeout
                try:
                    response = requests.head(ndl_url, timeout=1, allow_redirects=False)
                    if response.status_code in [200, 301, 302]:
                        return ndl_url
                except:
                    pass
            return ""
        except Exception:
            return ""
