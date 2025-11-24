# 推奨コマンド

## プロジェクトのセットアップ

```bash
# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 依存関係をインストール
pip install -e .

# 開発依存関係を含めてインストール
pip install -e ".[dev]"
```

## テスト

```bash
# すべてのテストを実行
pytest tests/ -v

# 特定のテストファイルを実行
pytest tests/test_book_service.py -v

# プロパティベーステストを実行
pytest tests/ -v -k "property"

# テストカバレッジを確認
pytest tests/ --cov=src --cov-report=html
```

## CLIコマンド

### 本の管理
```bash
# 本を登録（ISBNから自動取得）
hondana add-book 978-4-06-520808-7

# 登録されている本の一覧を表示
hondana list-books

# 本の詳細と感想を表示
hondana show-book <book_id>

# 本の情報を更新
hondana update-book <book_id> --title "新しいタイトル" --author "新しい著者"

# 本を削除（確認プロンプト付き）
hondana delete-book <book_id>
```

### 感想の管理
```bash
# 感想を投稿
hondana add-impression <book_id> "素晴らしい作品です"

# 感想を更新
hondana update-impression <impression_id> "更新された感想"

# 感想を削除
hondana delete-impression <impression_id>
```

### 静的サイト生成
```bash
# 静的HTMLサイトを生成（output/ディレクトリに出力）
hondana generate-site

# カスタム出力ディレクトリを指定
hondana generate-site --output /path/to/output
```

### v2 CLIコマンド（ステータス管理）
```bash
# 本のステータスを変更
hondana set-status <book_id> 読書中

# 本のステータスを表示
hondana show-status <book_id>

# 指定したステータスの本を一覧表示
hondana list-by-status 読了
```

### v2 CLIコマンド（Markdown感想管理）
```bash
# Markdown形式で感想を追加
hondana add-impression <book_id> "# 感想\n\n素晴らしい作品です"

# 感想を表示
hondana get-impression <book_id>

# 感想を更新
hondana update-impression <book_id> "# 更新された感想\n\n..."

# 感想を削除
hondana delete-impression <book_id>
```

## Webインターフェース

```bash
# Webアプリケーションを起動
python -m src.web_app

# ブラウザで http://localhost:5000 にアクセス
```

## システムユーティリティコマンド（Darwin/macOS）

```bash
# ファイル一覧
ls -la

# ディレクトリ移動
cd <directory>

# ファイル検索
find . -name "*.py"

# パターン検索
grep -r "pattern" .

# Git操作
git status
git add .
git commit -m "message"
git push
```

## データ移行

```python
from src.data_migration import DataMigration

# v1からv2へのデータ移行を実行
success = DataMigration.migrate_from_v1()
```
