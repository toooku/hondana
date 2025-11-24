"""Static site generator v2 with status grouping and cover images."""

import os
from typing import Dict, List
from src.models import Book
from src.book_service import BookService
from src.impression_service import ImpressionService
from src.markdown_impression_service import MarkdownImpressionService
from src.markdown_converter import MarkdownConverter


class StaticSiteGeneratorV2:
    """Generator for creating static HTML sites with v2 features."""

    def __init__(
        self,
        book_service: BookService,
        impression_service: ImpressionService,
        markdown_impression_service: MarkdownImpressionService,
        output_dir: str = "output"
    ):
        """Initialize the v2 static site generator.

        Args:
            book_service: BookService instance
            impression_service: ImpressionService instance (v1)
            markdown_impression_service: MarkdownImpressionService instance
            output_dir: Directory where HTML files will be generated
        """
        self.book_service = book_service
        self.impression_service = impression_service
        self.markdown_impression_service = markdown_impression_service
        self.output_dir = output_dir

    def generate(self) -> None:
        """Generate the static HTML site with v2 features."""
        os.makedirs(self.output_dir, exist_ok=True)
        books_dir = os.path.join(self.output_dir, "books")
        os.makedirs(books_dir, exist_ok=True)

        books = self.book_service.list_books()

        # 全ての本をランダムに並べ替える
        import random
        random.shuffle(books)

        self._generate_css()
        self._generate_index(books)

        for book in books:
            self._generate_book_page(book)

    def _generate_css(self) -> None:
        """Generate the CSS stylesheet with v2 styles - fullscreen tile layout."""
        css_content = """/* Stylesheet for book library v2 - Fullscreen tile layout */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    min-height: 100vh;
    overflow-x: hidden;
}

main {
    padding: 0;
    width: 100vw;
    min-height: 100vh;
}

.status-section {
    padding: 0;
}

.status-section h2 {
    display: none;
}

.book-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0;
    width: 100vw;
}

/* Tablet and larger */
@media (min-width: 768px) {
    .book-list {
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .book-list {
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    }
}

/* Large desktop */
@media (min-width: 1440px) {
    .book-list {
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    }
}

/* Ultra wide */
@media (min-width: 1920px) {
    .book-list {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    }
}

.book-card {
    background: #fff;
    border: 1px solid #e0e0e0;
    overflow: hidden;
    cursor: pointer;
    position: relative;
    aspect-ratio: 2/3;
}

.book-cover {
    width: 100%;
    height: 100%;
    background-color: #f8f8f8;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}

.book-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.book-cover-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    font-size: 0.85rem;
    text-align: center;
    padding: 1rem;
}

.book-info {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 50%, transparent 100%);
    padding: 0.5rem;
    opacity: 1;
}

.book-info h3 {
    font-size: 0.7rem;
    margin-bottom: 0.2rem;
    color: #333;
    font-weight: 600;
    line-height: 1.1;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.book-info .author {
    color: #666;
    font-size: 0.6rem;
    margin-bottom: 0.2rem;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.book-info .publisher {
    display: none;
}

.book-status {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    border-radius: 8px;
    font-size: 0.55rem;
    font-weight: bold;
    margin-top: 0.2rem;
}

.status-unread {
    background-color: #fff;
    color: #000;
    border: 1px solid #000;
}

.status-reading {
    background-color: #fff;
    color: #000;
    border: 1px solid #000;
}

.status-completed {
    background-color: #fff;
    color: #000;
    border: 1px solid #000;
}

.book-info a {
    display: none;
}

.book-detail {
    background: #fff;
    padding: 1rem;
    margin: 0;
    min-height: 100vh;
}

.book-detail-header {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    .book-detail-header {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}

.book-detail-cover {
    width: 200px;
    height: 300px;
    background-color: #f8f8f8;
    overflow: hidden;
    border: 1px solid #000;
}

@media (max-width: 768px) {
    .book-detail-cover {
        width: 100%;
        max-width: 250px;
        height: 375px;
        margin: 0 auto;
    }
}

.book-detail-cover img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.book-detail-info {
    padding: 0;
}

.book-detail-info h1 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: #000;
    font-weight: 600;
}

.book-detail-info p {
    margin-bottom: 0.5rem;
    color: #000;
    line-height: 1.4;
    font-size: 0.9rem;
}

.book-detail-info strong {
    color: #000;
}

.impressions {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #000;
}

.impressions h2 {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: #000;
    font-weight: 600;
}

.impression {
    background-color: #fff;
    padding: 0.5rem;
    margin-bottom: 0.5rem;
}

.impression-date {
    color: #000;
    font-size: 0.8rem;
    margin-bottom: 0.3rem;
}

.impression-content {
    color: #000;
    line-height: 1.6;
    font-size: 0.9rem;
}

.impression-content h1,
.impression-content h2,
.impression-content h3,
.impression-content h4,
.impression-content h5,
.impression-content h6 {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: #000;
    font-weight: 600;
    line-height: 1.3;
}

.impression-content h1 { font-size: 1.4rem; }
.impression-content h2 { font-size: 1.2rem; }
.impression-content h3 { font-size: 1.1rem; }

.impression-content p {
    margin-bottom: 1rem;
    line-height: 1.6;
}

.impression-content ul,
.impression-content ol {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

.impression-content li {
    margin-bottom: 0.25rem;
    line-height: 1.4;
}

.impression-content blockquote {
    border-left: 4px solid #ccc;
    padding-left: 1rem;
    margin: 1rem 0;
    color: #666;
    font-style: italic;
}

.impression-content code {
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    color: #d73a49;
    border: 1px solid #e1e4e8;
}

.impression-content pre {
    background-color: #f8f8f8;
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    border: 1px solid #e1e4e8;
    margin: 1rem 0;
}

.impression-content pre code {
    background-color: transparent;
    padding: 0;
    border: none;
    color: inherit;
}

.impression-content hr {
    border: none;
    border-top: 1px solid #e1e4e8;
    margin: 2rem 0;
}

.impression-content strong,
.impression-content b {
    font-weight: 600;
    color: #000;
}

.impression-content em,
.impression-content i {
    font-style: italic;
    color: #666;
}

.back-link {
    display: inline-block;
    margin: 1rem 0;
    padding: 0.5rem 1rem;
    background: #fff;
    color: #000;
    text-decoration: none;
    border: 1px solid #000;
    font-weight: 500;
    font-size: 0.9rem;
}
"""
        css_path = os.path.join(self.output_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)

    def _generate_index(self, books: List[Book]) -> None:
        """Generate the index page with all books in random order."""

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>蔵書管理</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <main>
        <h1>蔵書管理 ({len(books)}冊)</h1>
        <div class="book-list" id="book-list">
"""

        for book in books:
            cover_html = ""
            if book.cover_url:
                cover_html = f'<img src="{self._escape_html(book.cover_url)}" alt="{self._escape_html(book.title)}">'
            else:
                cover_html = f'<div class="book-cover-placeholder">書影なし</div>'

            html_content += f"""            <a href="books/{book.id}.html" style="text-decoration: none;">
                <div class="book-card">
                    <div class="book-cover">
                        {cover_html}
                    </div>
                    <div class="book-info">
                        <h3>{self._escape_html(book.title)}</h3>
                        <p class="author">{self._escape_html(book.author)}</p>
                        <p class="publisher">{self._escape_html(book.publisher)}</p>
                        <span class="book-status status-{self._get_status_class(book.status)}">{book.status}</span>
                    </div>
                </div>
            </a>
"""

        html_content += """
        </div>
    </main>
    <script>
        // ページ読み込み時に本の順序をランダムに並べ替える
        document.addEventListener('DOMContentLoaded', function() {
            const bookList = document.getElementById('book-list');
            const books = Array.from(bookList.children);

            // Fisher-Yates shuffle algorithm
            for (let i = books.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [books[i], books[j]] = [books[j], books[i]];
            }

            // 並べ替えた順序でDOMを更新
            books.forEach(book => bookList.appendChild(book));
        });
    </script>
</body>
</html>
"""

        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_book_page(self, book: Book) -> None:
        """Generate a detail page for a book with v2 features."""
        # Get impressions from both v1 and v2
        v1_impressions = self.impression_service.list_impressions_by_book(book.id)

        # Get Markdown impression
        markdown_content = self.markdown_impression_service.get_impression(book.id, book.title)

        cover_html = ""
        if book.cover_url:
            cover_html = f'<img src="{self._escape_html(book.cover_url)}" alt="{self._escape_html(book.title)}">'

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(book.title)}</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <main>
        <a href="../index.html" class="back-link">← 戻る</a>

        <div class="book-detail">
            <div class="book-detail-header">
                <div class="book-detail-cover">
                    {cover_html}
                </div>
                <div class="book-detail-info">
                    <h1>{self._escape_html(book.title)}</h1>
                    <p>著者: {self._escape_html(book.author)}</p>
                    <p>出版社: {self._escape_html(book.publisher)}</p>
                    <p>出版日: {book.publication_date}</p>
                    <p>ISBN: {self._escape_html(book.isbn)}</p>
                    <p>ステータス: <span class="book-status status-{self._get_status_class(book.status)}">{book.status}</span></p>
                    <p>登録日: {book.created_at}</p>
                    <p>説明: {self._escape_html(book.description)}</p>
                </div>
            </div>
"""

        # Add Markdown impression if exists
        if markdown_content:
            html_content += """            <div class="impressions">
                <h2>感想</h2>
"""
            html_content += f"""                <div class="impression">
                    <div class="impression-content">
                        {MarkdownConverter.convert_to_html(markdown_content)}
                    </div>
                </div>
"""
            html_content += """            </div>
"""

        # Add v1 impressions if exist
        if v1_impressions:
            if not markdown_content:
                html_content += """            <div class="impressions">
                <h2>感想</h2>
"""
            for impression in v1_impressions:
                html_content += f"""                <div class="impression">
                    <p class="impression-date">投稿日: {impression.created_at}</p>
                    <p class="impression-content">{self._escape_html(impression.content)}</p>
                </div>
"""
            if not markdown_content:
                html_content += """            </div>
"""

        html_content += """        </div>
    </main>
</body>
</html>
"""

        books_dir = os.path.join(self.output_dir, "books")
        book_page_path = os.path.join(books_dir, f"{book.id}.html")
        with open(book_page_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )


    @staticmethod
    def _get_status_class(status: str) -> str:
        """Get CSS class for status."""
        status_map = {
            "積読": "unread",
            "読書中": "reading",
            "読了": "completed"
        }
        return status_map.get(status, "unread")
