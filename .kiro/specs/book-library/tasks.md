# 蔵書管理アプリケーション - 実装計画

- [x] 1. プロジェクト構造とコア依存関係の設定
  - Pythonプロジェクトディレクトリ構造を作成（src/、tests/、data/、output/）
  - requirements.txtを作成し、必要なライブラリを指定（requests、hypothesis、click）
  - 基本的なプロジェクト設定ファイルを作成
  - _要件: 1.1, 2.1, 4.1, 5.1, 6.1_

- [x] 2. データモデルの実装
  - [x] 2.1 Bookクラスを実装（id、isbn、title、author、publisher、publication_date、description、created_at、updated_at）
    - UUIDの生成とISO 8601形式の日時処理を含める
    - _要件: 1.2_
  
  - [x] 2.2 Impressionクラスを実装（id、book_id、content、created_at、updated_at）
    - UUIDの生成とISO 8601形式の日時処理を含める
    - _要件: 4.1_
  
  - [x] 2.3 データモデルのプロパティテストを実装
    - **プロパティ1: 本の登録と取得の一貫性**
    - **検証: 要件1.2**

- [x] 3. OpenBD API統合の実装
  - [x] 3.1 OpenBDClientクラスを実装
    - fetch_book_info(isbn: str)メソッドを実装
    - ISBNが見つからない場合の例外処理を実装
    - ネットワークエラーのリトライロジックを実装
    - _要件: 1.1, 1.3_
  
  - [x] 3.2 OpenBD API統合のユニットテストを実装
    - 正常なレスポンスのテスト
    - ISBNが見つからない場合のテスト
    - ネットワークエラーのテスト

- [x] 4. 本管理サービスの実装
  - [x] 4.1 BookServiceクラスを実装
    - create_book(isbn: str)メソッド（OpenBD APIから情報取得）
    - get_book(book_id: str)メソッド
    - list_books()メソッド
    - update_book(book_id: str, **kwargs)メソッド
    - delete_book(book_id: str)メソッド（関連する感想も削除）
    - _要件: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2_
  
  - [x] 4.2 本管理サービスのプロパティテストを実装
    - **プロパティ2: 本の一覧にすべての本が含まれる**
    - **検証: 要件2.1**
  
  - [x] 4.3 本管理サービスのプロパティテストを実装
    - **プロパティ3: 本の詳細ページに必須情報が含まれる**
    - **検証: 要件2.3**
  
  - [x] 4.4 本管理サービスのプロパティテストを実装
    - **プロパティ4: 本の更新が反映される**
    - **検証: 要件3.1**
  
  - [x] 4.5 本管理サービスのプロパティテストを実装
    - **プロパティ5: 本の削除時に関連する感想も削除される**
    - **検証: 要件3.2**

- [x] 5. 感想管理サービスの実装
  - [x] 5.1 ImpressionServiceクラスを実装
    - create_impression(book_id: str, content: str)メソッド
    - get_impression(impression_id: str)メソッド
    - list_impressions_by_book(book_id: str)メソッド
    - update_impression(impression_id: str, content: str)メソッド
    - delete_impression(impression_id: str)メソッド
    - delete_impressions_by_book(book_id: str)メソッド
    - _要件: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 5.2 感想管理サービスのプロパティテストを実装
    - **プロパティ6: 感想の投稿と取得の一貫性**
    - **検証: 要件4.1**
  
  - [x] 5.3 感想管理サービスのプロパティテストを実装
    - **プロパティ7: 感想に投稿日時が記録される**
    - **検証: 要件4.2**
  
  - [x] 5.4 感想管理サービスのプロパティテストを実装
    - **プロパティ8: 感想の更新が反映される**
    - **検証: 要件4.3**
  
  - [x] 5.5 感想管理サービスのプロパティテストを実装
    - **プロパティ9: 感想の削除が反映される**
    - **検証: 要件4.4**

- [x] 6. データ永続化の実装
  - [x] 6.1 DataRepositoryクラスを実装
    - save_books(books: List[Book])メソッド
    - load_books() -> List[Book]メソッド
    - save_impressions(impressions: List[Impression])メソッド
    - load_impressions() -> List[Impression]メソッド
    - JSONファイルへの読み書きを実装
    - _要件: 6.1, 6.2_
  
  - [x] 6.2 データ永続化のプロパティテストを実装
    - **プロパティ12: データの永続化と復元の一貫性**
    - **検証: 要件6.2**

- [x] 7. チェックポイント - すべてのテストが成功していることを確認
  - すべてのテストが成功していることを確認し、問題があれば質問してください。

- [x] 8. 静的サイト生成の実装
  - [x] 8.1 StaticSiteGeneratorクラスを実装
    - generate()メソッド
    - index.html（本一覧ページ）の生成
    - books/{book_id}.html（本詳細ページ）の生成
    - style.css（最小限のスタイルシート）の生成
    - _要件: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 8.2 静的サイト生成のプロパティテストを実装
    - **プロパティ10: 静的サイト生成ですべての本がHTMLに含まれる**
    - **検証: 要件5.1**
  
  - [x] 8.3 静的サイト生成のプロパティテストを実装
    - **プロパティ11: 生成されたHTMLに本の詳細情報が含まれる**
    - **検証: 要件5.3**

- [x] 9. CLIインターフェースの実装
  - [x] 9.1 Clickを使用したCLIアプリケーションを実装
    - add-book <isbn>: 本を登録
    - list-books: 本一覧を表示
    - show-book <book_id>: 本の詳細と感想を表示
    - update-book <book_id>: 本の情報を更新
    - delete-book <book_id>: 本を削除（確認プロンプト付き）
    - _要件: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2_
  
  - [x] 9.2 感想管理CLIコマンドを実装
    - add-impression <book_id> <content>: 感想を投稿
    - update-impression <impression_id> <content>: 感想を更新
    - delete-impression <impression_id>: 感想を削除
    - _要件: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 9.3 静的サイト生成CLIコマンドを実装
    - generate-site: 静的HTMLサイトを生成
    - _要件: 5.1, 5.2, 5.3, 5.4_
  
  - [x] 9.4 CLIのユニットテストを実装
    - 各コマンドの正常系テスト
    - エラーハンドリングのテスト

- [x] 10. チェックポイント - すべてのテストが成功していることを確認
  - すべてのテストが成功していることを確認し、問題があれば質問してください。

- [x] 11. エラーハンドリングの実装
  - [x] 11.1 例外処理とエラーメッセージの実装
    - ISBNが見つからない場合のエラー処理
    - ネットワークエラーの処理
    - データファイル破損時のエラー処理
    - 入力検証エラーの処理
    - _要件: 1.3, 6.3_
  
  - [x] 11.2 エラーハンドリングのユニットテストを実装
    - 無効なISBNのテスト
    - 破損したデータファイルのテスト
    - 空の感想のテスト

- [x] 12. 最終チェックポイント - すべてのテストが成功していることを確認
  - すべてのテストが成功していることを確認し、問題があれば質問してください。
