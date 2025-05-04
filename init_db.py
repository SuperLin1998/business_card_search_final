import sqlite3

conn = sqlite3.connect('cards.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    phone TEXT,
    email TEXT,
    filename TEXT,
    created_at TEXT
)
''')

conn.commit()
conn.close()

print("✅ 資料庫 cards.db 建立成功")
