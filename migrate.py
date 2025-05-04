import sqlite3
from mydb.db_utils import save_to_postgres

def migrate():
    try:
        conn = sqlite3.connect('your_sqlite_file.db')  # 替換為實際 SQLite 檔案
        cursor = conn.cursor()

        cursor.execute("SELECT filename, raw_text FROM cards")
        rows = cursor.fetchall()

        success_count = 0
        for row in rows:
            filename, raw_text = row
            try:
                save_to_postgres(filename, raw_text)
                success_count += 1
            except Exception as e:
                print(f"[錯誤] 匯入資料失敗：{filename}，原因：{e}")

        print(f"✅ 成功匯入 {success_count} 筆資料")
    
    except sqlite3.OperationalError as e:
        print(f"[錯誤] SQLite 錯誤：{e}")
    
    except Exception as e:
        print(f"[錯誤] 無法完成資料轉移：{e}")

    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
