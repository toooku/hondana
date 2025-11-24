"""CLI interface for the book library application."""

from typing import Optional

import click

from src.book_service import BookService
from src.impression_service import ImpressionService
from src.markdown_impression_service import MarkdownImpressionService
from src.openbd_client import OpenBDClient
from src.repository import DataRepository
from src.static_site_generator_v2 import StaticSiteGeneratorV2


def get_services():
    """Get fresh service instances."""
    repository = DataRepository()
    markdown_impression_service = MarkdownImpressionService()
    book_service = BookService(repository, markdown_impression_service)
    impression_service = ImpressionService(repository)
    return book_service, impression_service, markdown_impression_service


@click.group()
def cli():
    """蔵書管理アプリケーション - 本と感想を管理するCLIツール"""
    pass


# ============================================================================
# Book Management Commands
# ============================================================================


@cli.command()
@click.argument("isbn")
def add_book(isbn: str):
    """ISBNから本を登録します。

    Args:
        isbn: 本のISBN
    """
    try:
        book_service, _, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    try:
        book = book_service.create_book(isbn)
        click.echo(f"✓ 本を登録しました")
        click.echo(f"  ID: {book.id}")
        click.echo(f"  タイトル: {book.title}")
        click.echo(f"  著者: {book.author}")
        click.echo(f"  出版社: {book.publisher}")
    except book_service.ISBNAlreadyExistsError as e:
        click.echo(f"✗ ISBN重複エラー: {str(e)}", err=True)
        raise SystemExit(1)
    except OpenBDClient.ISBNNotFoundError:
        click.echo(f"✗ エラー: ISBN '{isbn}' が見つかりません", err=True)
        raise SystemExit(1)
    except OpenBDClient.NetworkError as e:
        click.echo(f"✗ ネットワークエラー: {str(e)}", err=True)
        raise SystemExit(1)


@cli.command()
def list_books():
    """登録されている本の一覧を表示します。"""
    try:
        book_service, _, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    books = book_service.list_books()

    if not books:
        click.echo("登録されている本がありません")
        return

    click.echo(f"\n登録されている本 ({len(books)}件):\n")

    # Display as table
    for book in books:
        click.echo(f"ID: {book.id}")
        click.echo(f"  タイトル: {book.title}")
        click.echo(f"  著者: {book.author}")
        click.echo(f"  出版社: {book.publisher}")
        click.echo(f"  出版日: {book.publication_date}")
        click.echo(f"  ISBN: {book.isbn}")
        click.echo(f"  登録日: {book.created_at}")
        click.echo()


@cli.command()
@click.argument("book_id")
def show_book(book_id: str):
    """本の詳細情報と感想を表示します。

    Args:
        book_id: 本のID
    """
    try:
        book_service, impression_service, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    book = book_service.get_book(book_id)

    if not book:
        click.echo(f"✗ エラー: ID '{book_id}' の本が見つかりません", err=True)
        raise SystemExit(1)

    # Display book details
    click.echo(f"\n【本の詳細】\n")
    click.echo(f"ID: {book.id}")
    click.echo(f"タイトル: {book.title}")
    click.echo(f"著者: {book.author}")
    click.echo(f"出版社: {book.publisher}")
    click.echo(f"出版日: {book.publication_date}")
    click.echo(f"ISBN: {book.isbn}")
    click.echo(f"登録日: {book.created_at}")
    click.echo(f"説明: {book.description}")

    # Display impressions
    impressions = impression_service.list_impressions_by_book(book_id)

    if impressions:
        click.echo(f"\n【感想 ({len(impressions)}件)】\n")
        for impression in impressions:
            click.echo(f"ID: {impression.id}")
            click.echo(f"投稿日: {impression.created_at}")
            click.echo(f"内容: {impression.content}")
            click.echo()
    else:
        click.echo(f"\n感想がまだ投稿されていません")


@cli.command()
@click.argument("book_id")
@click.option("--title", default=None, help="新しいタイトル")
@click.option("--author", default=None, help="新しい著者")
@click.option("--publisher", default=None, help="新しい出版社")
@click.option("--publication-date", default=None, help="新しい出版日")
@click.option("--description", default=None, help="新しい説明")
def update_book(
    book_id: str,
    title: Optional[str],
    author: Optional[str],
    publisher: Optional[str],
    publication_date: Optional[str],
    description: Optional[str],
):
    """本の情報を更新します。

    Args:
        book_id: 本のID
    """
    try:
        book_service, _, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    book = book_service.get_book(book_id)

    if not book:
        click.echo(f"✗ エラー: ID '{book_id}' の本が見つかりません", err=True)
        raise SystemExit(1)

    # Build update dict
    updates = {}
    if title:
        updates["title"] = title
    if author:
        updates["author"] = author
    if publisher:
        updates["publisher"] = publisher
    if publication_date:
        updates["publication_date"] = publication_date
    if description:
        updates["description"] = description

    if not updates:
        click.echo("✗ エラー: 更新する項目を指定してください", err=True)
        raise SystemExit(1)

    updated_book = book_service.update_book(book_id, **updates)
    click.echo(f"✓ 本を更新しました")
    click.echo(f"  ID: {updated_book.id}")
    click.echo(f"  タイトル: {updated_book.title}")


@cli.command()
@click.argument("book_id")
@click.option("--confirm", is_flag=True, help="確認プロンプトをスキップ")
def delete_book(book_id: str, confirm: bool):
    """本を削除します（関連する感想も削除されます）。

    Args:
        book_id: 本のID
    """
    try:
        book_service, impression_service, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    book = book_service.get_book(book_id)

    if not book:
        click.echo(f"✗ エラー: ID '{book_id}' の本が見つかりません", err=True)
        raise SystemExit(1)

    # Show confirmation prompt
    if not confirm:
        click.echo(f"\n本を削除します:")
        click.echo(f"  タイトル: {book.title}")
        click.echo(f"  著者: {book.author}")

        impressions = impression_service.list_impressions_by_book(book_id)
        if impressions:
            click.echo(f"\n関連する感想 ({len(impressions)}件) も削除されます")

        if not click.confirm("\n本当に削除しますか？"):
            click.echo("キャンセルしました")
            return

    # Delete impressions first
    deleted_impressions = impression_service.delete_impressions_by_book(book_id)

    # Delete book
    book_service.delete_book(book_id)

    click.echo(f"✓ 本を削除しました")
    if deleted_impressions > 0:
        click.echo(f"  関連する感想 {deleted_impressions}件 も削除されました")


# ============================================================================
# Impression Management Commands
# ============================================================================


@cli.command()
@click.argument("book_id")
@click.argument("content")
def add_impression(book_id: str, content: str):
    """感想を投稿します。

    Args:
        book_id: 本のID
        content: 感想の内容
    """
    try:
        book_service, impression_service, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    book = book_service.get_book(book_id)

    if not book:
        click.echo(f"✗ エラー: ID '{book_id}' の本が見つかりません", err=True)
        raise SystemExit(1)

    try:
        impression = impression_service.create_impression(book_id, content)
        click.echo(f"✓ 感想を投稿しました")
        click.echo(f"  ID: {impression.id}")
        click.echo(f"  本: {book.title}")
        click.echo(f"  投稿日: {impression.created_at}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("impression_id")
@click.argument("content")
def update_impression(impression_id: str, content: str):
    """感想を更新します。

    Args:
        impression_id: 感想のID
        content: 新しい感想の内容
    """
    try:
        _, impression_service, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    impression = impression_service.get_impression(impression_id)

    if not impression:
        click.echo(f"✗ エラー: ID '{impression_id}' の感想が見つかりません", err=True)
        raise SystemExit(1)

    try:
        updated_impression = impression_service.update_impression(
            impression_id, content
        )
        click.echo(f"✓ 感想を更新しました")
        click.echo(f"  ID: {updated_impression.id}")
        click.echo(f"  更新日: {updated_impression.updated_at}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument("impression_id")
@click.option("--confirm", is_flag=True, help="確認プロンプトをスキップ")
def delete_impression(impression_id: str, confirm: bool):
    """感想を削除します。

    Args:
        impression_id: 感想のID
    """
    try:
        book_service, impression_service, _ = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    impression = impression_service.get_impression(impression_id)

    if not impression:
        click.echo(f"✗ エラー: ID '{impression_id}' の感想が見つかりません", err=True)
        raise SystemExit(1)

    # Show confirmation prompt
    if not confirm:
        book = book_service.get_book(impression.book_id)
        click.echo(f"\n感想を削除します:")
        click.echo(f"  本: {book.title if book else 'Unknown'}")
        click.echo(f"  内容: {impression.content[:50]}...")

        if not click.confirm("\n本当に削除しますか？"):
            click.echo("キャンセルしました")
            return

    impression_service.delete_impression(impression_id)
    click.echo(f"✓ 感想を削除しました")


# ============================================================================
# Static Site Generation Commands
# ============================================================================


@cli.command()
@click.option("--output", default="output", help="出力ディレクトリ")
def generate_site(output: str):
    """静的HTMLサイトを生成します。

    Args:
        output: 出力ディレクトリ
    """
    try:
        book_service, impression_service, markdown_impression_service = get_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)

    try:
        generator = StaticSiteGeneratorV2(
            book_service=book_service,
            impression_service=impression_service,
            markdown_impression_service=markdown_impression_service,
            output_dir=output,
        )
        generator.generate()

        books = book_service.list_books()
        click.echo(f"✓ 静的サイトを生成しました")
        click.echo(f"  出力先: {output}/")
        click.echo(f"  本の数: {len(books)}")
        click.echo(f"  生成ファイル:")
        click.echo(f"    - index.html (本一覧ページ)")
        click.echo(f"    - books/*.html (本詳細ページ)")
        click.echo(f"    - style.css (スタイルシート)")
    except Exception as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
