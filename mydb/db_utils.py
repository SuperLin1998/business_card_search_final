import psycopg2
import os
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            database=os.getenv('PG_DB'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            port=int(os.getenv('PG_PORT', 5432))  # 預設 port 為 5432
            
        )
        return conn
    except Exception as e:
        print("❌ 連接資料庫失敗：", e)
        raise

def save_to_postgres(filename, raw_text):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO cards (filename, raw_text)
            VALUES (%s, %s)
        ''', (filename, raw_text))
        conn.commit()
        print("✅ 資料已成功儲存至 PostgreSQL")
    except Exception as e:
        print("❌ 儲存資料失敗：", e)
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
