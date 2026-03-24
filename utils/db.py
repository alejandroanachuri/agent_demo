import sqlite3

conn = sqlite3.connect(
    "news.db",
    check_same_thread=False,
    timeout=5
)

conn.execute("PRAGMA journal_mode=WAL;")

cursor = conn.cursor()
def generate_tables():
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS news
    USING FTS5(
        title,
        summary,
        url,
        source,
        date
    )
    """)
    print("Creating embedding table")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_embeddings (
        url TEXT PRIMARY KEY,
        embedding TEXT
    )
    """)
    conn.commit()
