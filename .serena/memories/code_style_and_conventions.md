# コードスタイルと規約

## 言語とバージョン

- Python 3.8以上
- UTF-8エンコーディング

## 命名規則

- **クラス名**: PascalCase（例: `Book`, `BookService`, `StatusHistory`）
- **関数・メソッド名**: スネークケース（例: `create_book`, `get_book`, `list_books`）
- **変数名**: スネークケース（例: `book_id`, `cover_url`）
- **プライベート属性**: アンダースコアで始める（例: `_books`）

## 型ヒント

- すべての関数・メソッドに型ヒントを使用
- 戻り値の型を明示（例: `-> dict`, `-> "Book"`, `-> None`）
- 引数にも型ヒントを付与

例:
```python
def to_dict(self) -> dict:
    """Convert the Book instance to a dictionary."""
    ...

@classmethod
def from_dict(cls, data: dict) -> "Book":
    """Create a Book instance from a dictionary."""
    ...
```

## Docstring

- すべてのクラス、メソッド、関数にdocstringを記述
- トリプルクォート（`"""`）を使用
- 簡潔で明確な説明を記述

例:
```python
class Book:
    """Represents a book in the library."""
    ...

def to_dict(self) -> dict:
    """Convert the Book instance to a dictionary."""
    ...
```

## データクラス

- データモデルには`@dataclass`デコレータを使用
- `field(default_factory=...)`を使用してデフォルト値を設定

例:
```python
@dataclass
class Book:
    """Represents a book in the library."""
    isbn: str
    title: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
```

## インポート順序

- 標準ライブラリ
- サードパーティライブラリ
- ローカルモジュール

## コメント

- 日本語のコメントを使用可能（プロジェクト内で日本語が使用されている）
- 複雑なロジックには説明コメントを追加

## エラーハンドリング

- 適切な例外処理を実装
- ユーザーフレンドリーなエラーメッセージを提供

## テスト

- ユニットテストとプロパティベーステスト（Hypothesis）を使用
- テストファイルは`tests/`ディレクトリに配置
- テストファイル名は`test_*.py`形式
