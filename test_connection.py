import psycopg2

try:
    conn = psycopg2.connect(
        host="34.81.63.188",
        database="postgres",  # 資料庫名稱不是實例名稱
        user="postgres",  # 使用你的 Cloud SQL > 使用者帳戶 中的使用者
        password="20250503",
        port=5432
    )
    print("✅ 成功連線到 PostgreSQL")
    conn.close()
except Exception as e:
    print("❌ 無法連線：", e)
