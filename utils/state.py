import sqlite3
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging
import logging

hf_logging.set_verbosity_error()
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

model = SentenceTransformer("all-MiniLM-L6-v2")
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS news_embeddings (
    url TEXT PRIMARY KEY,
    title TEXT,
    summary TEXT,                      
    embedding TEXT,
    date           
)
""")
conn.commit()

que_pasa_jujuy_index = []
infobae_index = []
connection = conn
cursor = cursor