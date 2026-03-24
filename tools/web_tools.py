import requests
import json
import numpy as np
from bs4 import BeautifulSoup
from agents import function_tool
from newspaper import Article, Config
from urllib.parse import urljoin
from utils import state
from datetime import date

@function_tool
def search_news_que_pasa_jujuy(topic: str) -> list:
    """
    Busca noticias en la base de datos usando una busqueda full-text 
    del diario que pasa jujuy.
    """
    print('searching in que pasa Jujuy')
    return db_search('quepasajujuy', topic)

@function_tool
def search_news_infobae(topic: str) -> list:
    """
    Busca noticias en el indice actual del diario Infobae con noticias nacionales.
    """
    print('Searching in Infobae..')
    return db_search('infobae', topic)

@function_tool
def read_article(url):
    """
    Lee un articulo en particular del diario digital, esta funcion extrae la informacion de la nota
    """
    print('Read article...')
    config = Config()
    config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    article = Article(url, config=config)
    article.download()
    article.parse()

    return article.text

def clean_query(q: str):
    return q.replace("?", "").replace("¿", "").strip().lower()
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def db_search(source, topic):
    today = date.today().isoformat()
    topic = clean_query(topic)
    try:
        print("Buscando FTS5.....")
        state.cursor.execute("""
            SELECT title, summary, url
            FROM news
            WHERE news MATCH ?
            AND date = ?
            AND source = ?
            ORDER BY bm25(news)
            LIMIT 10
            """, (topic, today, source))
        
        fts_rows  = state.cursor.fetchall()
        print("Registros encontrados:",rows)
    except: 
        fts_rows = []    
        
    semantic_results = []
    try:
        print("Buscando en seamantic search....")
        query_embedding = state.model.encode(topic)
        state.cursor.execute("""
        SELECT title, summary, url, embedding
        FROM news_embeddings
        WHERE date = ?
        """, (today,))
        rows = state.cursor.fetchall()
        scored = []

        for r in rows:
            try:
                emb = np.array(json.loads(r[3]))
                score = cosine_similarity(query_embedding, emb)
                #if score > 0.4:
                scored.append((score, r))
            except:
                continue

        scored.sort(reverse=True, key=lambda x: x[0])
        semantic_results = [
            {
                "title": r[1][0],
                "summary": r[1][1],
                "url": r[1][2],
                "score": float(r[0])
            }
            for r in scored[:10]
        ]
    except Exception as e:
        print("[TOOL ERROR - SEMANTIC]", e)

    # convertir FTS a dict
    fts_results = [
        {
            "title": r[0],
            "summary": r[1],
            "url": r[2],
            "score": 1.0  # score base
        }
        for r in fts_rows
    ]

    # combinar (evitar duplicados por URL)
    combined = {}
    for item in fts_results:
        combined[item["url"]] = item

    for item in semantic_results:
        if item["url"] in combined:
            # boost si aparece en ambos
            combined[item["url"]]["score"] += item["score"]
        else:
            combined[item["url"]] = item
    
    final_results = list(combined.values())
    # ordenar por score
    final_results.sort(reverse=True, key=lambda x: x["score"])

    #Fallback
    if len(final_results) < 3:
        print("FAllback no encontre match")
        state.cursor.execute("""
            SELECT title, summary, url
            FROM news
            WHERE date = ?
            AND source = ?               
            LIMIT 10
            """, (today,source))
        
        rows = state.cursor.fetchall()
        final_results = [
            {
                "title": r[0],
                "summary": r[1],
                "url": r[2]
            }
            for r in rows
        ]
    # quitar score antes de devolver
    final_results = [
        {
            "title": r["title"],
            "summary": r["summary"],
            "url": r["url"]
        }
        for r in final_results[:10]
    ]
    print(f"[TOOL] returning {len(final_results)} results")
    return final_results
