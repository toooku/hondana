"""Static site generator for creating HTML output from books and impressions."""

import os
from typing import List
from src.models import Book, Impression
from src.book_service import BookService
from src.impression_service import ImpressionService


class StaticSiteGenerator:
    """Generator for creating static HTML sites from books and impressions."""

    def __init__(
        self,
        book_service: BookService,
        impression_service: ImpressionService,
        output_dir: str = "output"
    ):
        """
        Initialize the static site generator.

        Args:
            book_service: BookService instance for accessing books
            impression_service: ImpressionService instance for accessing impressions
            output_dir: Directory where HTML files will be generated
        """
        self.book_service = book_service
        self.impression_service = impression_service
        self.output_dir = output_dir

    def generate(self) -> None:
        """Generate the static HTML site."""
        # Create output directory structure
        os.makedirs(self.output_dir, exist_ok=True)
        books_dir = os.path.join(self.output_dir, "books")
        os.makedirs(books_dir, exist_ok=True)

        # Generate CSS
        self._generate_css()

        # Generate index page
        self._generate_index()

        # Generate book detail pages
        books = self.book_service.list_books()
        for book in books:
            self._generate_book_page(book)

    def _generate_css(self) -> None:
        """Generate the CSS stylesheet."""
        css_content = """/* Minimal stylesheet for book library */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f9f9f9;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 2rem;
    text-align: center;
}

header h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.book-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

.book-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.3s ease;
}

.book-card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.book-card h2 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    color: #2c3e50;
}

.book-card .author {
    color: #7f8c8d;
    font-style: italic;
    margin-bottom: 0.5rem;
}

.book-card .publisher {
    color: #95a5a6;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.book-card .date {
    color: #95a5a6;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

.book-card a {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.book-card a:hover {
    background-color: #2980b9;
}

.book-detail {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.book-detail h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.book-info {
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid #ecf0f1;
}

.book-info p {
    margin-bottom: 0.5rem;
}

.book-info strong {
    color: #2c3e50;
}

.impressions {
    margin-top: 2rem;
}

.impressions h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.impression {
    background-color: #f9f9f9;
    border-left: 4px solid #3498db;
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 4px;
}

.impression-date {
    color: #95a5a6;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

.impression-content {
    color: #333;
    line-height: 1.6;
}

.back-link {
    display: inline-block;
    margin-bottom: 2rem;
    padding: 0.5rem 1rem;
    background-color: #95a5a6;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.back-link:hover {
    background-color: #7f8c8d;
}

footer {
    background-color: #2c3e50;
    color: white;
    text-align: center;
    padding: 2rem;
    margin-top: 4rem;
}
"""
        css_path = os.path.join(self.output_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)

    def _generate_index(self) -> None:
        """Generate the index (list) page."""
        books = self.book_service.list_books()

        html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>蔵書管理 - 本一覧</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>蔵書管理</h1>
        <p>個人の蔵書を管理・閲覧するサイト</p>
    </header>

    <main>
        <div class="book-list">
"""

        for book in books:
            html_content += f"""            <div class="book-card">
                <h2>{self._escape_html(book.title)}</h2>
                <p class="author">{self._escape_html(book.author)}</p>
                <p class="publisher">{self._escape_html(book.publisher)}</p>
                <p class="date">{book.publication_date}</p>
                <a href="books/{book.id}.html">詳細を見る</a>
            </div>
"""

        html_content += """        </div>
    </main>

    <footer>
        <p>&copy; 2024 蔵書管理アプリケーション</p>
    </footer>
</body>
</html>
"""

        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_book_page(self, book: Book) -> None:
        """
        Generate a detail page for a specific book.

        Args:
            book: The Book instance to generate a page for
        """
        impressions = self.impression_service.list_impressions_by_book(
            book.id
        )

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(book.title)} - 蔵書管理</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header>
        <h1>蔵書管理</h1>
    </header>

    <main>
        <a href="../index.html" class="back-link">← 一覧に戻る</a>

        <div class="book-detail">
            <h1>{self._escape_html(book.title)}</h1>

            <div class="book-info">
                <p><strong>著者:</strong> {self._escape_html(book.author)}</p>
                <p><strong>出版社:</strong> {self._escape_html(book.publisher)}</p>
                <p><strong>出版日:</strong> {book.publication_date}</p>
                <p><strong>ISBN:</strong> {self._escape_html(book.isbn)}</p>
                <p><strong>登録日:</strong> {book.created_at}</p>
                <p><strong>説明:</strong></p>
                <p>{self._escape_html(book.description)}</p>
            </div>
"""

        if impressions:
            html_content += """            <div class="impressions">
                <h2>感想</h2>
"""
            for impression in impressions:
                html_content += f"""                <div class="impression">
                    <p class="impression-date">投稿日: {impression.created_at}</p>
                    <p class="impression-content">{self._escape_html(impression.content)}</p>
                </div>
"""
            html_content += """            </div>
"""

        html_content += """        </div>
    </main>

    <footer>
        <p>&copy; 2024 蔵書管理アプリケーション</p>
    </footer>
</body>
</html>
"""

        books_dir = os.path.join(self.output_dir, "books")
        book_page_path = os.path.join(books_dir, f"{book.id}.html")
        with open(book_page_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    @staticmethod
    def _escape_html(text: str) -> str:
        """
        Escape HTML special characters.

        Args:
            text: The text to escape

        Returns:
            The escaped text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )
