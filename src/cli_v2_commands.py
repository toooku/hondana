"""CLI commands for book library v2 features."""

import click
from src.status_service import StatusService
from src.markdown_impression_service import MarkdownImpressionService
from src.repository import DataRepository
from src.book_service import BookService


def get_v2_services():
    """Get v2 service instances."""
    repository = DataRepository()
    book_service = BookService(repository)
    status_service = StatusService(repository)
    markdown_impression_service = MarkdownImpressionService()
    return book_service, status_service, markdown_impression_service


@click.group()
def status_commands():
    """ステータス管理コマンド"""
    pass


@status_commands.command()
@click.argument("book_id")
@click.argument("status")
def set_status(book_id: str, status: str):
    """本の読書ステータスを変更します。

    Args:
        book_id: 本のID
        status: 新しいステータス (積読/読書中/読了)
    """
    try:
        _, status_service, _ = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        book = status_service.set_status(book_id, status)
        click.echo(f"✓ ステータスを変更しました")
        click.echo(f"  本: {book.title}")
        click.echo(f"  新しいステータス: {book.status}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@status_commands.command()
@click.argument("book_id")
def show_status(book_id: str):
    """本の読書ステータスを表示します。

    Args:
        book_id: 本のID
    """
    try:
        _, status_service, _ = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        status = status_service.get_status(book_id)
        history = status_service.get_status_history(book_id)
        
        click.echo(f"現在のステータス: {status}")
        
        if history:
            click.echo(f"\nステータス変更履歴:")
            for h in history:
                click.echo(f"  {h.changed_at}: {h.old_status} → {h.new_status}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@status_commands.command()
@click.argument("status")
def list_by_status(status: str):
    """指定したステータスの本を一覧表示します。

    Args:
        status: ステータス (積読/読書中/読了)
    """
    try:
        book_service, status_service, _ = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        books = status_service.get_books_by_status(status)
        
        if not books:
            click.echo(f"ステータス '{status}' の本がありません")
            return
        
        click.echo(f"\nステータス '{status}' の本 ({len(books)}冊):\n")
        
        for book in books:
            click.echo(f"  {book.title}")
            click.echo(f"    著者: {book.author}")
            click.echo(f"    ID: {book.id}")
            click.echo()
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@click.group()
def impression_commands():
    """感想管理コマンド"""
    pass


@impression_commands.command()
@click.argument("book_id")
@click.argument("content")
def add_impression(book_id: str, content: str):
    """本に感想を追加します（Markdown形式）。

    Args:
        book_id: 本のID
        content: 感想のテキスト
    """
    try:
        book_service, _, markdown_impression_service = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        # Verify book exists
        book = book_service.get_book(book_id)
        
        # Create impression
        impression = markdown_impression_service.create_impression(book_id, content)
        click.echo(f"✓ 感想を追加しました")
        click.echo(f"  本: {book.title}")
        click.echo(f"  感想ID: {impression.id}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@impression_commands.command()
@click.argument("book_id")
def get_impression(book_id: str):
    """本の感想を表示します。

    Args:
        book_id: 本のID
    """
    try:
        book_service, _, markdown_impression_service = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        # Verify book exists
        book = book_service.get_book(book_id)
        
        # Get impression
        content = markdown_impression_service.get_impression(book_id)
        
        if not content:
            click.echo(f"本 '{book.title}' の感想がありません")
            return
        
        click.echo(f"本: {book.title}\n")
        click.echo(content)
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@impression_commands.command()
@click.argument("book_id")
@click.argument("content")
def update_impression(book_id: str, content: str):
    """本の感想を更新します。

    Args:
        book_id: 本のID
        content: 新しい感想のテキスト
    """
    try:
        book_service, _, markdown_impression_service = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        # Verify book exists
        book = book_service.get_book(book_id)
        
        # Update impression
        impression = markdown_impression_service.update_impression(book_id, content)
        click.echo(f"✓ 感想を更新しました")
        click.echo(f"  本: {book.title}")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)


@impression_commands.command()
@click.argument("book_id")
def delete_impression(book_id: str):
    """本の感想を削除します。

    Args:
        book_id: 本のID
    """
    try:
        book_service, _, markdown_impression_service = get_v2_services()
    except IOError as e:
        click.echo(f"✗ データエラー: {str(e)}", err=True)
        raise SystemExit(1)
    
    try:
        # Verify book exists
        book = book_service.get_book(book_id)
        
        # Delete impression
        deleted = markdown_impression_service.delete_impression(book_id)
        
        if deleted:
            click.echo(f"✓ 感想を削除しました")
            click.echo(f"  本: {book.title}")
        else:
            click.echo(f"本 '{book.title}' の感想がありません")
    except ValueError as e:
        click.echo(f"✗ エラー: {str(e)}", err=True)
        raise SystemExit(1)
