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
- **連続登録モード**: バーコードスキャンで自動的に本を連続登録
- **読書ステータス管理**: 積読、読書中、読了の3つのステータスで読書進捗を管理
- **ステータス履歴**: 読書ステータスの変更履歴を自動記録
- **書影表示**: OpenBD APIから取得した本の表紙画像を表示
- **Markdownベースの感想管理**: 長い感想をMarkdownファイルで管理
- **Webインターフェース**: Flask を使用したWebUIでブラウザから操作可能
- **本の削除**: WEB UIから本と関連感想を削除可能
- **アクセス時ランダム表示**: 静的サイトアクセス時に本の並び順がランダムに変わる
- **データ移行**: v1からv2への自動データ移行機能

## インストール

### 前提条件

- Python 3.8以上
- uv または pip

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd hondana

# uvを使用する場合（推奨）
uv sync
source .venv/bin/activate  # macOS/Linux

# または従来のpipを使用する場合
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

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

### AWSへの自動デプロイ

GitHub Actionsを使ってmainブランチへのプッシュ時に自動的にAWSにデプロイできます。

**注意**: AWSデプロイでは実際の蔵書データを使用します。個人情報が公開される可能性があるため、必要な場合のみ有効化してください。

#### セットアップ

1. AWSリソースを作成（S3バケット + CloudFront）
2. GitHubリポジトリのSecretsを設定
3. mainブランチにプッシュすると自動デプロイ

#### デプロイ先URL

- **S3のみ**: `http://your-bucket-name.s3-website-region.amazonaws.com`
- **CloudFront使用**: `https://distribution-id.cloudfront.net`

#### データについて

デプロイされるサイトには`data/`ディレクトリ内の実際の蔵書データが使用されます。感想データも含めて公開されます。

#### ⚠️ セキュリティ警告

- **個人情報公開**: 蔵書データに個人情報が含まれる場合、インターネット上で公開されます
- **感想データの公開**: 個人的な感想が誰でも閲覧可能になります
- **データバックアップ**: AWS公開前に必ずデータをバックアップしてください
- **公開範囲**: 必要最小限の期間のみ公開し、不要になったら削除してください

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

# ブラウザで http://localhost:8000 にアクセス
```

Webインターフェースの機能：
- ホームページ: ランダム順に並べ替えられた本の表示
- 本一覧: ステータスごとに分類された本の表示
- 本詳細: 書影、ステータス、感想の表示と削除機能
- ステータス変更: Webから直接ステータスを変更
- バーコード読み取り: Webカメラを使用したISBN読み取りと連続登録モード
- 本の追加: スキャンまたは手動入力による本の登録
- 本の削除: WEB UIから本と関連感想を削除
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
│   ├── markdown_impression_service.py   # Markdown感想管理（v2）
│   ├── markdown_converter.py            # Markdown→HTML変換（v2）
│   ├── static_site_generator_v2.py      # HTML生成（v2）
│   ├── web_app.py                       # Webインターフェース（v2）
│   ├── data_migration.py                # データ移行ユーティリティ（v2）
│   └── cli.py                           # CLIインターフェース（統合）
├── tests/
│   ├── __init__.py
│   ├── test_book_service.py             # 本管理テスト
│   ├── test_cli.py                      # CLIテスト
│   ├── test_error_handling.py           # エラーハンドリングテスト
│   ├── test_impression_service.py       # 感想管理テスト
│   ├── test_models.py                   # モデルテスト
│   ├── test_openbd_client.py            # API統合テスト
│   └── test_static_site_generator.py    # HTML生成テスト
├── data/
│   ├── books.json                       # 本のデータ
│   ├── status_history.json              # ステータス変更履歴（v2）
│   └── impressions/                     # Markdown感想ファイル（v2）
│       └── *.md
├── output/                              # 生成されたHTMLサイト
│   ├── index.html
│   ├── books/
│   │   └── *.html
│   └── style.css
├── pyproject.toml                       # プロジェクト設定
├── requirements.txt                     # 依存関係
├── uv.lock                              # uv依存関係ロックファイル
└── README.md                            # このファイル
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

### impressions/{title}_{book_id}.md（v2）

```markdown
# 書名: ノルウェイの森

（ユーザーが自由に感想を書く）
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
- **pyzbar**: バーコード読み取り（ZXingライブラリ）
- **opencv-python**: カメラアクセス（Webカメラ連携）
- **markdown**: Markdown→HTML変換
- **Flask**: Webインターフェース
- **pytest**: テストフレームワーク（開発時）
- **pytest-cov**: カバレッジ測定（開発時）

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