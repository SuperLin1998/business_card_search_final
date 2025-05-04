import sqlite3
import os

# SQLite 資料庫位置
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cards.db')

def search_cards(keyword):
    """從 SQLite 搜尋名片資料（以 raw_text 為搜尋目標）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 用 LIKE 模糊查詢
    cursor.execute('''
        SELECT filename, raw_text
        FROM cards
        WHERE raw_text LIKE ?
        ORDER BY created_at DESC
    ''', (f'%{keyword}%',))

    results = cursor.fetchall()
    conn.close()

    return results
