import sqlite3
import os

# SQLite 資料庫位置
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cards.db')

def search_cards(keyword):
    """從 SQLite 根據關鍵字模糊搜尋"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = '''
        SELECT filename, raw_text
        FROM cards
        WHERE raw_text LIKE ?
        ORDER BY created_at DESC
    '''
    cursor.execute(query, ('%' + keyword + '%',))
    rows = cursor.fetchall()
    conn.close()
    return rows
