"""Flask web application for book library v2."""

from flask import Flask, redirect, request, url_for

from src.book_service import BookService
from src.markdown_impression_service import MarkdownImpressionService
from src.repository import DataRepository
from src.status_service import StatusService

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# Constants
STATUS_LABELS = {"積読": "積読", "読書中": "読書中", "読了": "読了"}
STATUS_CLASSES = {"積読": "unread", "読書中": "reading", "読了": "completed"}

# Initialize services
repository = DataRepository()
book_service = BookService(repository)
status_service = StatusService(repository)
markdown_impression_service = MarkdownImpressionService()


def generate_cover_html(book):
    """Generate cover image HTML for a book."""
    if book.cover_url:
        return f"""<div style="width: 300px; height: 400px; background: #f0f0f0; border-radius: 4px; margin: 20px 0; display: flex; align-items: center; justify-content: center; overflow: hidden;">
            <img src="{book.cover_url}" alt="{book.title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;" onerror="this.parentElement.innerHTML='<div style=\\'color: #999;\\'>書影なし</div>'">
        </div>"""
    return '<div style="width: 300px; height: 400px; background: #f0f0f0; border-radius: 4px; margin: 20px 0; display: flex; align-items: center; justify-content: center;"><div style="color: #999;">書影なし</div></div>'


def generate_status_select(book):
    """Generate status selection form HTML."""
    options = []
    for status_value, status_label in STATUS_LABELS.items():
        selected = "selected" if book.status == status_value else ""
        options.append(
            f'<option value="{status_value}" {selected}>{status_label}</option>'
        )

    return f"""
    <h2>ステータス変更</h2>
    <form method="POST" action="/books/{book.id}/status">
        <select name="status">
            {"".join(options)}
        </select>
        <button type="submit">変更</button>
    </form>
    """


def generate_delete_form(book):
    """Generate book deletion form HTML."""
    return f"""
    <h2>本の削除</h2>
    <p style="color: #c62828;"><strong>注意:</strong> この操作は取り消せません。本と関連する感想も削除されます。</p>
    <form method="POST" action="/books/{book.id}/delete" onsubmit="return confirm('本当にこの本を削除しますか？')">
        <button type="submit" style="background: #c62828; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer;">本を削除</button>
    </form>
    """


# Fetch missing cover URLs for existing books
try:
    book_service.fetch_missing_cover_urls()
except Exception:
    # Silently ignore errors during cover URL fetching
    pass


@app.route("/")
def index():
    """Home page."""
    import random

    books = book_service.list_books()

    # 全ての本をランダムに並べ替える
    original_order = [book.title for book in books]
    random.shuffle(books)
    shuffled_order = [book.title for book in books]

    app.logger.info(f"Original order: {original_order}")
    app.logger.info(f"Shuffled order: {shuffled_order}")
    app.logger.info(f"Order changed: {original_order != shuffled_order}")

    # ステータス別の本数を計算
    status_counts = {}
    for book in books:
        status = book.status
        status_counts[status] = status_counts.get(status, 0) + 1

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>蔵書管理 - ホーム</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            .section {{ margin: 20px 0; }}
            .book-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
            .book-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 8px; }}
            .book-card h3 {{ margin: 0 0 10px 0; }}
            .book-card p {{ margin: 5px 0; font-size: 0.9em; }}
            .status {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }}
            .status-unread {{ background: #e8f4f8; color: #0277bd; }}
            .status-reading {{ background: #fff3e0; color: #e65100; }}
            .status-completed {{ background: #e8f5e9; color: #2e7d32; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>蔵書管理</h1>
        <nav>
            <a href="/books">本一覧</a> |
            <a href="/scan">バーコード読み取り</a> |
            <a href="/generate-site">サイト生成</a>
        </nav>
        <div class="section">
            <h2>蔵書数: {len(books)}冊</h2>
            <div class="book-list">
    """

    # 全ての本を表示
    for book in books:
        cover_html = ""
        if book.cover_url:
            cover_html = f"""<div style="width: 100%; height: 200px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                <img src="{book.cover_url}" alt="{book.title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;" onerror="this.parentElement.innerHTML='<div style=\\'color: #999; font-size: 0.9em;\\'>書影なし</div>'">
            </div>"""
        else:
            cover_html = '<div style="width: 100%; height: 200px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center;"><div style="color: #999; font-size: 0.9em;">書影なし</div></div>'

        status_class = {"積読": "unread", "読書中": "reading", "読了": "completed"}.get(
            book.status, "unread"
        )

        html += f"""
            <div class="book-card">
                {cover_html}
                <h3>{book.title}</h3>
                <p><strong>著者:</strong> {book.author}</p>
                <p><strong>出版社:</strong> {book.publisher}</p>
                <p><span class="status status-{status_class}">{book.status}</span></p>
                <a href="/books/{book.id}">詳細</a>
            </div>
        """

    html += """
        </div>
    </div>
    </body>
    </html>
    """
    return html


@app.route("/books")
def books_list():
    """List all books."""
    books = book_service.list_books()
    books_by_status = {
        "積読": [b for b in books if b.status == "積読"],
        "読書中": [b for b in books if b.status == "読書中"],
        "読了": [b for b in books if b.status == "読了"],
    }

    html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>本一覧</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            .section { margin: 30px 0; }
            .book-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
            .book-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; }
            .book-card h3 { margin: 0 0 10px 0; }
            .book-card p { margin: 5px 0; font-size: 0.9em; }
            .status { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }
            .status-unread { background: #e8f4f8; color: #0277bd; }
            .status-reading { background: #fff3e0; color: #e65100; }
            .status-completed { background: #e8f5e9; color: #2e7d32; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>本一覧</h1>
        <a href="/">← ホームに戻る</a>
    """

    for status, label in [
        ("積読", "積読（未読）"),
        ("読書中", "読書中"),
        ("読了", "読了"),
    ]:
        books_in_status = books_by_status[status]
        if not books_in_status:
            continue

        status_class = {"積読": "unread", "読書中": "reading", "読了": "completed"}[
            status
        ]
        html += f"""
        <div class="section">
            <h2>{label} ({len(books_in_status)}冊)</h2>
            <div class="book-list">
        """

        for book in books_in_status:
            cover_html = ""
            if book.cover_url:
                cover_html = f"""<div style="width: 100%; height: 200px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                    <img src="{book.cover_url}" alt="{book.title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;" onerror="this.parentElement.innerHTML='<div style=\\'color: #999; font-size: 0.9em;\\'>書影なし</div>'">
                </div>"""
            else:
                cover_html = '<div style="width: 100%; height: 200px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center;"><div style="color: #999; font-size: 0.9em;">書影なし</div></div>'

            html += f"""
                <div class="book-card">
                    {cover_html}
                    <h3>{book.title}</h3>
                    <p><strong>著者:</strong> {book.author}</p>
                    <p><strong>出版社:</strong> {book.publisher}</p>
                    <p><span class="status status-{status_class}">{status}</span></p>
                    <a href="/books/{book.id}">詳細</a>
                </div>
            """

        html += """
            </div>
        </div>
        """

    html += """
    </body>
    </html>
    """
    return html


@app.route("/books/<book_id>")
def book_detail(book_id):
    """Show book detail."""
    try:
        book = book_service.get_book(book_id)
    except ValueError:
        return "Book not found", 404

    try:
        impression = markdown_impression_service.get_impression(book_id)
    except Exception:
        impression = None

    status_class = {"積読": "unread", "読書中": "reading", "読了": "completed"}.get(
        book.status, "unread"
    )

    cover_html = generate_cover_html(book)

    html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>{book.title}</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            .status {{ display: inline-block; padding: 5px 10px; border-radius: 3px; }}
            .status-unread {{ background: #e8f4f8; color: #0277bd; }}
            .status-reading {{ background: #fff3e0; color: #e65100; }}
            .status-completed {{ background: #e8f5e9; color: #2e7d32; }}
            .impression {{ background: #f9f9f9; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            button {{ padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #2980b9; }}
        </style>
    </head>
    <body>
        <a href="/books">← 本一覧に戻る</a>
        <h1>{book.title}</h1>
        {cover_html}
        <p><strong>著者:</strong> {book.author}</p>
        <p><strong>出版社:</strong> {book.publisher}</p>
        <p><strong>ISBN:</strong> {book.isbn}</p>
        <p><strong>ステータス:</strong> <span class="status status-{status_class}">{book.status}</span></p>
        <p><strong>説明:</strong> {book.description}</p>
        
        {generate_status_select(book)}
        {generate_delete_form(book)}
    """

    if impression:
        html += f"""
        <h2>感想</h2>
        <div class="impression">
            {impression}
        </div>
        """

    html += """
    </body>
    </html>
    """
    return html


@app.route("/books/<book_id>/status", methods=["POST"])
def update_status(book_id):
    """Update book status."""
    new_status = request.form.get("status")
    try:
        status_service.set_status(book_id, new_status)
        return redirect(url_for("book_detail", book_id=book_id))
    except ValueError as e:
        return f"Error: {str(e)}", 400


@app.route("/books/<book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book."""
    try:
        # Delete the book from database
        book_service.delete_book(book_id)

        # Also delete the associated Markdown impression file
        markdown_impression_service.delete_impression(book_id)

        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>本を削除しました</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .success {{ background: #e8f5e9; padding: 20px; border-radius: 4px; color: #2e7d32; }}
                a {{ color: #3498db; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✓ 本を削除しました</h1>
                <p>本と関連する感想ファイルが削除されました。</p>
                <p><a href="/books">本一覧に戻る</a></p>
                <p><a href="/">ホームに戻る</a></p>
            </div>
        </body>
        </html>
        """
    except ValueError as e:
        return (
            f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .error {{ background: #ffebee; padding: 20px; border-radius: 4px; color: #c62828; }}
                a {{ color: #3498db; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>✗ エラーが発生しました</h1>
                <p>{str(e)}</p>
                <p><a href="/books/{book_id}">本の詳細に戻る</a></p>
            </div>
        </body>
        </html>
        """,
            400,
        )


@app.route("/scan")
def scan():
    """Barcode scanning page."""
    return """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>バーコード読み取り</title>
    <script src="https://cdn.jsdelivr.net/npm/@zxing/library@0.20.0/umd/index.min.js"></script>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        .info { background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .controls { margin: 20px 0; }
        .mode-selector { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .mode-selector label { margin-right: 15px; }
        button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        button:hover { background: #2980b9; }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
        #video { width: 100%; max-width: 500px; border: 2px solid #3498db; margin: 20px 0; display: none; }
        .isbn-input { padding: 10px; font-size: 1em; width: 300px; }
        a { color: #3498db; text-decoration: none; }
        .result { margin: 20px 0; padding: 15px; border-radius: 4px; display: none; }
        .result.success { background: #e8f5e9; color: #2e7d32; border: 1px solid #2e7d32; }
        .result.error { background: #ffebee; color: #c62828; border: 1px solid #c62828; }
        .toast { position: fixed; top: 20px; right: 20px; padding: 15px 20px; border-radius: 4px; color: white; font-weight: bold; z-index: 1000; opacity: 0; transition: opacity 0.3s; }
        .toast.success { background: #4caf50; }
        .toast.error { background: #f44336; }
        .toast.show { opacity: 1; }
        .book-counter { margin: 10px 0; padding: 10px; background: #e8f4f8; border-radius: 4px; display: none; }
        .book-counter span { font-weight: bold; color: #0277bd; }
    </style>
</head>
<body>
    <a href="/">← ホームに戻る</a>
    <h1>バーコード読み取り</h1>
    <div class="info">
        <p>カメラからISBNバーコードを読み取ります。</p>
        <p>バーコードをカメラに向けてください。</p>
    </div>

    <div class="mode-selector">
        <h3>登録モード</h3>
        <label><input type="radio" name="mode" value="single" checked> 単一登録モード</label>
        <label><input type="radio" name="mode" value="continuous"> 連続登録モード</label>
        <div class="book-counter" id="bookCounter">
            登録した本の数: <span id="bookCount">0</span>冊
        </div>
    </div>

    <div class="controls">
        <button id="startBtn" onclick="startCamera()">カメラを起動</button>
        <button id="stopBtn" onclick="stopCamera()" disabled>カメラを停止</button>
        <button id="resetBtn" onclick="resetCounter()" style="background: #95a5a6;">カウンターをリセット</button>
    </div>
    
    <video id="video" width="500" height="400"></video>
    <div id="result" class="result"></div>

    <h2>ISBN入力</h2>
    <form method="POST" action="/add-book-from-isbn" id="isbnForm">
        <input type="text" id="isbnInput" name="isbn" class="isbn-input" placeholder="ISBNを入力またはスキャンしてください" required>
        <button type="submit">本を登録</button>
    </form>

    <!-- Toast notification -->
    <div id="toast" class="toast"></div>
    
    <script>
        const codeReader = new ZXing.BrowserMultiFormatReader();
        let stream = null;
        let scanning = false;
        let bookCount = 0;
        let processedISBNs = new Set(); // 重複登録防止用

        // モード切り替えイベント
        document.querySelectorAll('input[name="mode"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const isContinuous = this.value === 'continuous';
                document.getElementById('bookCounter').style.display = isContinuous ? 'block' : 'none';
                if (!isContinuous) {
                    resetCounter();
                }
            });
        });

        async function startCamera() {
            try {
                const videoElement = document.getElementById('video');
                videoElement.style.display = 'block';

                const result = await codeReader.decodeFromVideoDevice(
                    undefined,
                    videoElement,
                    (result, err) => {
                        if (result) {
                            const isbn = result.text.replace(/[^0-9]/g, '');
                            if ((isbn.length === 10 || isbn.length === 13) && !processedISBNs.has(isbn)) {
                                handleISBNDetection(isbn);
                            }
                        }
                    }
                );

                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                scanning = true;
                showResult('カメラが起動しました。バーコードを向けてください。', 'success');
            } catch (err) {
                showResult('カメラへのアクセスが拒否されました: ' + err.message, 'error');
            }
        }

        function stopCamera() {
            codeReader.reset();
            document.getElementById('video').style.display = 'none';
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            scanning = false;
            showResult('', '');
        }

        async function handleISBNDetection(isbn) {
            const isContinuous = document.querySelector('input[name="mode"]:checked').value === 'continuous';

            if (isContinuous) {
                // 連続モード：自動登録
                processedISBNs.add(isbn);
                await addBookAutomatically(isbn);
            } else {
                // 単一モード：フォームにセットして手動登録
                document.getElementById('isbnInput').value = isbn;
                showResult('✓ ISBNを検出しました: ' + isbn, 'success');
                stopCamera();
            }
        }

        async function addBookAutomatically(isbn) {
            try {
                const response = await fetch('/api/add-book-from-isbn', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ isbn: isbn })
                });

                const result = await response.json();

                if (result.success) {
                    bookCount++;
                    updateCounter();
                    showToast('✓ ' + result.book.title + ' を登録しました', 'success');
                } else {
                    if (response.status === 409) {
                        showToast('⚠ この本は既に登録されています', 'error');
                    } else {
                        showToast('✗ 登録エラー: ' + result.error, 'error');
                    }
                }
            } catch (error) {
                showToast('✗ 通信エラー: ' + error.message, 'error');
            }
        }

        function showResult(message, type) {
            let resultDiv = document.getElementById('result');
            if (message) {
                resultDiv.textContent = message;
                resultDiv.className = 'result ' + type;
                resultDiv.style.display = 'block';
            } else {
                resultDiv.style.display = 'none';
            }
        }

        function showToast(message, type) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast ' + type + ' show';

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        function updateCounter() {
            document.getElementById('bookCount').textContent = bookCount;
        }

        function resetCounter() {
            bookCount = 0;
            processedISBNs.clear();
            updateCounter();
            showToast('カウンターをリセットしました', 'success');
        }

        // フォーム送信時の処理（単一モード用）
        document.getElementById('isbnForm').addEventListener('submit', function(e) {
            const isbn = document.getElementById('isbnInput').value;
            if (isbn) {
                processedISBNs.add(isbn);
            }
        });
    </script>
</body>
</html>"""


@app.route("/add-book-from-isbn", methods=["POST"])
def add_book_from_isbn():
    """Add book from ISBN input."""
    try:
        isbn = request.form.get("isbn", "").strip() if request.form else ""
    except Exception:
        isbn = ""

    if not isbn:
        return "ISBNを入力してください", 400

    try:
        book = book_service.create_book(isbn)
        return f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>本を登録しました</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .success {{ background: #e8f5e9; padding: 20px; border-radius: 4px; color: #2e7d32; }}
                a {{ color: #3498db; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✓ 本を登録しました</h1>
                <p><strong>タイトル:</strong> {book.title}</p>
                <p><strong>著者:</strong> {book.author}</p>
                <p><strong>出版社:</strong> {book.publisher}</p>
                <p><a href="/books/{book.id}">本の詳細を見る</a></p>
                <p><a href="/scan">別の本を登録</a></p>
                <p><a href="/">ホームに戻る</a></p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return (
            f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>エラー</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                .error {{ background: #ffebee; padding: 20px; border-radius: 4px; color: #c62828; }}
                a {{ color: #3498db; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>✗ エラーが発生しました</h1>
                <p>{str(e)}</p>
                <p><a href="/scan">バーコード読み取りに戻る</a></p>
            </div>
        </body>
        </html>
        """,
            400,
        )


@app.route("/api/add-book-from-isbn", methods=["POST"])
def api_add_book_from_isbn():
    """API endpoint to add book from ISBN (returns JSON)."""
    try:
        data = request.get_json() if request.is_json else request.form
        isbn = data.get("isbn", "").strip() if data else ""

        if not isbn:
            return {"success": False, "error": "ISBNを入力してください"}, 400

        book = book_service.create_book(isbn)

        return {
            "success": True,
            "book": {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "isbn": book.isbn,
            },
        }

    except book_service.ISBNAlreadyExistsError as e:
        return {"success": False, "error": str(e)}, 409
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.route("/generate-site")
def generate_site_page():
    """Generate site page."""
    html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>サイト生成</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1em; }
            button:hover { background: #2980b9; }
            a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <a href="/">← ホームに戻る</a>
        <h1>静的サイト生成</h1>
        <p>登録されている本と感想から静的HTMLサイトを生成します。</p>
        <form method="POST" action="/generate-site">
            <button type="submit">サイトを生成</button>
        </form>
    </body>
    </html>
    """
    return html


@app.route("/generate-site", methods=["POST"])
def generate_site():
    """Generate static site."""
    try:
        from src.impression_service import ImpressionService
        from src.static_site_generator_v2 import StaticSiteGeneratorV2

        # Create v1 impression service for compatibility
        impression_service = ImpressionService(repository)

        generator = StaticSiteGeneratorV2(
            book_service, impression_service, markdown_impression_service
        )
        generator.generate()
        return "サイトを生成しました。output/index.htmlを確認してください。"
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
