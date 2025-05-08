from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
from extractor import extract_text  # 新增
from mydb.db_utils import save_to_postgres, get_connection # 新增
from mydb import db_utils
from psycopg2.extras import RealDictCursor
from google.cloud import storage, secretmanager, vision
from dotenv import load_dotenv

import os
import tempfile

   

load_dotenv()  # 確保 Flask 啟動時能讀到 .env

def test_vision_with_secret():
        
        # 初始化 Secret Manager 客戶端
        sm_client = secretmanager.SecretManagerServiceClient()
        
        # 設定 Secret 路徑 (使用您的 Secret ID)
        project_id = "mysqlproject20250503"  # 替換為您的專案 ID
        secret_id = "visionapikey20250508"  # 您的 Secret ID
        version_id = "latest"
        
        secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        print(f"正在訪問 Secret: {secret_path}")
        
        # 訪問 Secret 內容
        response = sm_client.access_secret_version(name=secret_path)
        secret_payload = response.payload.data.decode('UTF-8')
        
        # 將 Secret 寫入臨時檔案
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(secret_payload)
            credentials_path = temp_file.name
        
        
        # 設定憑證環境變數
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # 清理臨時檔案
        os.unlink(credentials_path)
        return True, print("API完成")

# 自動抓取環境變數設定的金鑰
client = storage.Client()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'KEY'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/other', methods=['GET', 'POST'])
def other():
    return render_template('other.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # 第二階段：使用者確認編輯後的文字
        if 'corrected_text' in request.form:
            fn = request.form['filename']
            text = request.form['corrected_text']
            save_to_postgres(fn, text)
            flash('已成功儲存！')
            return redirect(url_for('search'))

        # 第一階段：上傳圖片並進行 Google Vision OCR
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('請選擇檔案')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('檔案類型不支援')
            return redirect(request.url)

        fn = secure_filename(file.filename)

        # 檢查檔案是否已存在於資料庫
        conn = db_utils.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards WHERE filename = %s", (fn,))
        count = cursor.fetchone()[0]
        conn.close()

        if count > 0:
            flash('此名片已上傳，請勿重複上傳。')
            return redirect(request.url)

        # 儲存圖片檔案
        path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
        file.save(path)

        try:
            ocr_text = extract_text(path)
        except Exception as e:
            flash(f'辨識失敗：{e}')
            return redirect(request.url)

        return render_template('upload.html', filename=fn, ocr_text=ocr_text)

    return render_template('upload.html')



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()

        if not keyword:
            # 如果關鍵字是空的，導回自己
            return redirect(url_for('search'))

        # 連線資料庫
        conn = db_utils.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)


        # 搜尋 raw_text
        query = "SELECT id, filename, raw_text, created_at FROM cards WHERE raw_text LIKE %s"
        cursor.execute(query, (f'%{keyword}%',))
        rows = cursor.fetchall()
        conn.close()

        # 把 rows 轉成 list of dict（因為 row_factory 已經設好）
        results = [
            {
                'id': row['id'],
                'filename': row['filename'],
                'raw_text': row['raw_text'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

        return render_template('search.html', results=results, keyword=keyword)

    return render_template('search.html', results=[], keyword='')

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/list')
def list_cards():
    conn = db_utils.get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)


    cursor.execute('SELECT id, filename, raw_text, created_at FROM cards')
    rows = cursor.fetchall()
    conn.close()

    cards = [
        {
            'id': row['id'],
            'filename': row['filename'],
            'raw_text': row['raw_text'],
            'created_at': row['created_at']
        }
        for row in rows
    ]

    return render_template('list.html', cards=cards)


@app.route('/delete/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    # 連線資料庫
    conn = db_utils.get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)


    # 查詢對應資料與圖片名稱
    cursor.execute("SELECT filename FROM cards WHERE id = %s", (card_id,))
    row = cursor.fetchone()

    if row:
        filename = row['filename']
        # 刪除資料庫資料
        cursor.execute("DELETE FROM cards WHERE id = %s", (card_id,))
        conn.commit()
        conn.close()

        # 刪除圖片檔案
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(img_path):
            os.remove(img_path)

        flash('已成功刪除名片資訊與圖片。')
    else:
        flash('找不到對應的名片。')

    return redirect(url_for('search'))


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
