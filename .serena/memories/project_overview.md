# プロジェクト概要

## プロジェクト名

hondana（蔵書管理アプリケーション）

## プロジェクトの目的

個人の蔵書を管理・閲覧するための静的サイト生成型アプリケーション。ISBNを使用して本を登録し、OpenBD APIから書誌情報を自動取得。本ごとに感想を投稿でき、管理画面で本と感想のCRUD操作が可能。最終的には静的HTMLサイトとして公開できます。

## 技術スタック

### コアライブラリ
- **requests**: HTTP通信（OpenBD API連携）
- **click**: CLIフレームワーク
- **Flask**: Webインターフェース（v2）

### v2機能のライブラリ
- **pyzbar**: バーコード読み取り
- **opencv-python**: カメラアクセス
- **markdown**: Markdown→HTML変換

### テスト
- **pytest**: テストフレームワーク
- **hypothesis**: プロパティベーステスト

## プロジェクト構造

```
hondana/
├── src/
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
│   └── cli_v2_commands.py              # CLIコマンド（v2）
├── tests/                               # テストファイル
├── data/                                # データファイル（JSON、Markdown）
│   ├── books.json
│   ├── impressions.json
│   ├── status_history.json
│   └── impressions/                     # Markdown感想ファイル
├── output/                              # 生成されたHTMLサイト
├── pyproject.toml                       # プロジェクト設定
└── requirements.txt                     # 依存関係
```

## 主要機能

### v1 機能
- 本の登録（ISBNから自動取得）
- 本の管理（CRUD操作）
- 感想の管理（CRUD操作）
- 静的サイト生成
- CLIインターフェース
- データ永続化（JSON）

### v2 新機能
- バーコード読み取り（Webカメラ）
- 読書ステータス管理（積読、読書中、読了）
- ステータス履歴
- 書影表示
- Markdownベースの感想管理
- Webインターフェース（Flask）
- データ移行（v1→v2）

## エントリーポイント

- **CLI**: `hondana` コマンド（`src.cli:cli`から実行）
- **Webアプリ**: `python -m src.web_app`

## データ形式

- **books.json**: 本のデータ（v2形式では`cover_url`と`status`フィールドを含む）
- **status_history.json**: 読書ステータスの変更履歴
- **impressions.json**: 感想のデータ（v1形式）
- **impressions/{book_id}.md**: Markdown形式の感想（v2形式）

## テスト戦略

- **ユニットテスト**: 特定の例とエッジケースを検証
- **プロパティベーステスト**: Hypothesisライブラリを使用してランダムデータで普遍的な性質を検証

## 開発環境

- **OS**: Darwin（macOS）
- **Python**: 3.8以上
- **パッケージ管理**: pip または uv
- **仮想環境**: venv（推奨）
