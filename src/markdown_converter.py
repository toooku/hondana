"""Markdown to HTML converter."""

from typing import Optional

import markdown


class MarkdownConverter:
    """Converter for transforming Markdown to HTML."""

    @staticmethod
    def convert_to_html(markdown_text: str) -> str:
        """Convert Markdown text to HTML.

        Args:
            markdown_text: Markdown formatted text

        Returns:
            HTML formatted text
        """
        if not markdown_text:
            return ""

        try:
            html = markdown.markdown(
                markdown_text, extensions=["extra", "codehilite", "toc"]
            )
            return html
        except Exception:
            # If conversion fails, return escaped text
            return f"<p>{markdown_text}</p>"

    @staticmethod
    def wrap_in_html_document(html_content: str, title: str = "Document") -> str:
        """Wrap HTML content in a complete HTML document.

        Args:
            html_content: HTML content to wrap
            title: Title for the HTML document

        Returns:
            Complete HTML document
        """
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        code {{
            background-color: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 16px;
            color: #666;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
