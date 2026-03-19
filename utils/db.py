import sqlite3

conn = sqlite3.connect(
    "news.db",
    check_same_thread=False,
    timeout=5
)

conn.execute("PRAGMA journal_mode=WAL;")

cursor = conn.cursor()
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
conn.commit()
