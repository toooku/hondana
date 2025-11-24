# 蔵書管理アプリケーション (hondana)

個人の蔵書を管理・閲覧するための静的サイト生成型アプリケーション。ISBNを使用して本を登録し、OpenBD APIから書誌情報を自動取得。本ごとに感想を投稿でき、管理画面で本と感想のCRUD操作が可能。最終的には静的HTMLサイトとして公開できます。

## 機能

### v1 機能
- **本の登録**: ISBNから自動的に書誌情報を取得（OpenBD API連携）
- **本の管理**: 本の一覧表示、詳細表示、更新、削除
- **感想の管理**: 本ごとに感想を投稿、編集、削除
- **静的サイト生成**: 登録した本と感想をHTMLサイトとして生成
- **CLIインターフェース**: コマンドラインから簡単に操作可能
- **データ永続化**: JSONファイルにデータを保存

### v2 新機能
- **バーコード読み取り**: Webカメラを使用してISBNバーコードを自動認識
- **読書ステータス管理**: 積読、読書中、読了の3つのステータスで読書進捗を管理
- **ステータス履歴**: 読書ステータスの変更履歴を自動記録
- **書影表示**: OpenBD APIから取得した本の表紙画像を表示
- **Markdownベースの感想管理**: 長い感想をMarkdownファイルで管理
- **Webインターフェース**: Flask を使用したWebUIでブラウザから操作可能
- **データ移行**: v1からv2への自動データ移行機能

## インストール

### 前提条件

- Python 3.8以上
- pip または uv

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd hondana

# 仮想環境を作成（推奨）
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -e .
```

## 使い方

### CLIコマンド

#### 本の管理

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

#### 感想の管理

```bash
# 感想を投稿
hondana add-impression <book_id> "素晴らしい作品です"

# 感想を更新
hondana update-impression <impression_id> "更新された感想"

# 感想を削除
hondana delete-impression <impression_id>
```

#### 静的サイト生成

```bash
# 静的HTMLサイトを生成（output/ディレクトリに出力）
hondana generate-site

# カスタム出力ディレクトリを指定
hondana generate-site --output /path/to/output
```

### v2 CLIコマンド

#### ステータス管理

```bash
# 本のステータスを変更
hondana set-status <book_id> 読書中

# 本のステータスを表示
hondana show-status <book_id>

# 指定したステータスの本を一覧表示
hondana list-by-status 読了
```

#### Markdown感想管理

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

### Webインターフェース

```bash
# Webアプリケーションを起動
python -m src.web_app

# ブラウザで http://localhost:5000 にアクセス
```

Webインターフェースの機能：
- ホームページ: ステータス別の本数表示
- 本一覧: ステータスごとに分類された本の表示
- 本詳細: 書影、ステータス、感想の表示
- ステータス変更: Webから直接ステータスを変更
- バーコード読み取り: Webカメラを使用したISBN読み取り
- サイト生成: Webから静的サイトを生成

## プロジェクト構造

```
hondana/
├── src/
│   ├── __init__.py
│   ├── models.py                        # データモデル（Book, Impression, StatusHistory）
│   ├── repository.py                    # データ永続化
│   ├── openbd_client.py                 # OpenBD API統合
│   ├── book_service.py                  # 本管理ロジック
│   ├── impression_service.py            # 感想管理ロジック（v1）
│   ├── status_service.py                # ステータス管理ロジック（v2）
│   ├── barcode_scanner.py               # バーコード読み取り（v2）
│   ├── markdown_impression_service.py   # Markdown感想管理（v2）
│   ├── markdown_converter.py            # Markdown→HTML変換（v2）
│   ├── static_site_generator.py         # HTML生成（v1）
│   ├── static_site_generator_v2.py      # HTML生成（v2）
│   ├── web_app.py                       # Webインターフェース（v2）
│   ├── data_migration.py                # データ移行ユーティリティ（v2）
│   ├── cli.py                           # CLIインターフェース（v1）
│   └── cli_v2_commands.py               # CLIコマンド（v2）
├── tests/
│   ├── test_models.py                   # モデルテスト
│   ├── test_repository.py               # リポジトリテスト
│   ├── test_openbd_client.py            # API統合テスト
│   ├── test_book_service.py         # 本管理テスト
│   ├── test_impression_service.py   # 感想管理テスト
│   ├── test_static_site_generator.py # HTML生成テスト
│   ├── test_cli.py                  # CLIテスト
│   └── test_error_handling.py       # エラーハンドリングテスト
├── data/
│   ├── books.json                   # 本のデータ
│   └── impressions.json             # 感想のデータ
├── output/                          # 生成されたHTMLサイト
├── pyproject.toml                   # プロジェクト設定
├── requirements.txt                 # 依存関係
└── README.md                        # このファイル
```

## データ形式

### books.json（v2形式）

```json
[
  {
    "id": "uuid-1",
    "isbn": "978-4-06-520808-7",
    "title": "ノルウェイの森",
    "author": "村上春樹",
    "publisher": "新潮社",
    "publication_date": "1987-09-04",
    "description": "...",
    "cover_url": "https://cover.openbd.jp/...",
    "status": "読了",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### status_history.json（v2）

```json
[
  {
    "id": "uuid-2",
    "book_id": "uuid-1",
    "old_status": "積読",
    "new_status": "読書中",
    "changed_at": "2024-01-16T10:00:00Z"
  }
]
```

### impressions/{book_id}.md（v2）

```markdown
# ノルウェイの森 - 感想

## 全体的な印象
素晴らしい作品。深い思考を促される。

## 好きなシーン
- 主人公とナオコの会話シーン
- 森での瞑想シーン

## 感想
この作品は...
```

### impressions.json

```json
[
  {
    "id": "uuid-2",
    "book_id": "uuid-1",
    "content": "素晴らしい作品。深い思考を促される。",
    "created_at": "2024-01-16T14:20:00Z",
    "updated_at": "2024-01-16T14:20:00Z"
  }
]
```

## テスト

### すべてのテストを実行

```bash
pytest tests/ -v
```

### 特定のテストファイルを実行

```bash
pytest tests/test_book_service.py -v
```

### プロパティベーステストを実行

```bash
pytest tests/ -v -k "property"
```

### テストカバレッジを確認

```bash
pytest tests/ --cov=src --cov-report=html
```

## テスト戦略

このプロジェクトは、**ユニットテスト**と**プロパティベーステスト（PBT）**の両方を使用して、ソフトウェアの正確性を検証しています。

### ユニットテスト

- 特定の例とエッジケースを検証
- 統合ポイントの動作確認
- エラーハンドリングの検証

### プロパティベーステスト

- Hypothesisライブラリを使用
- ランダムに生成されたデータに対して普遍的な性質を検証
- 各プロパティは100回以上実行

#### 実装されたプロパティ

1. **本の登録と取得の一貫性**: 登録した本の情報がすべて保持される
2. **本の一覧にすべての本が含まれる**: 登録されたすべての本が一覧に表示される
3. **本の詳細ページに必須情報が含まれる**: 必須情報がすべて表示される
4. **本の更新が反映される**: 更新した情報が正しく反映される
5. **本の削除時に関連する感想も削除される**: 本削除時に関連データも削除される
6. **感想の投稿と取得の一貫性**: 投稿した感想が正しく取得される
7. **感想に投稿日時が記録される**: 投稿日時が自動的に記録される
8. **感想の更新が反映される**: 更新した感想が正しく反映される
9. **感想の削除が反映される**: 削除した感想は取得できなくなる
10. **静的サイト生成ですべての本がHTMLに含まれる**: すべての本がHTMLに含まれる
11. **生成されたHTMLに本の詳細情報が含まれる**: 詳細情報がすべて含まれる
12. **データの永続化と復元の一貫性**: 保存したデータが正しく復元される

## エラーハンドリング

アプリケーションは以下のエラーに対応しています：

- **ISBNが見つからない**: OpenBD APIから情報が取得できない場合、ユーザーフレンドリーなエラーメッセージを表示
- **ネットワークエラー**: APIリクエストがタイムアウトした場合、リトライロジックを実装
- **データファイルの破損**: JSONパースエラーが発生した場合、エラーログを出力
- **入力検証**: 空の感想、無効なISBNなどの入力を検証

## v1からv2へのアップグレード

### データ移行

v1のデータをv2形式に自動移行できます：

```python
from src.data_migration import DataMigration

# v1からv2へのデータ移行を実行
success = DataMigration.migrate_from_v1()

if success:
    print("データ移行が完了しました")
else:
    print("データ移行に失敗しました")
```

移行内容：
- v1の本データに `cover_url` と `status` フィールドを追加
- v1の感想データをMarkdownファイルに変換
- ステータス履歴ファイルを初期化

## 依存関係

- **requests**: HTTP通信（OpenBD API連携）
- **hypothesis**: プロパティベーステスト
- **click**: CLIフレームワーク
- **pytest**: テストフレームワーク
- **pyzbar**: バーコード読み取り（v2）
- **opencv-python**: カメラアクセス（v2）
- **markdown**: Markdown→HTML変換（v2）
- **Flask**: Webインターフェース（v2）

## 開発

### 開発環境のセットアップ

```bash
pip install -e ".[dev]"
```

### コードスタイル

このプロジェクトはPythonの標準的なコーディング規約に従っています。

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## サポート

問題が発生した場合は、GitHubのissueを作成してください。