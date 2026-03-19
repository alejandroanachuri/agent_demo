import requests
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


def db_search(source, topic):
    today = date.today().isoformat()
    print(topic)
    try:
        state.cursor.execute("""
            SELECT title, summary, url
            FROM news
            WHERE news MATCH ?
            AND date = ?
            AND source = ?
            ORDER BY bm25(news)
            LIMIT 10
            """, (topic, today, source))
        
        rows = state.cursor.fetchall()
        print("Registros encontrados:",rows)
        if not rows:
            print("FAllback no encontre match")
            state.cursor.execute("""
            SELECT title, summary, url
            FROM news
            WHERE date = ?
            AND source = ?               
            LIMIT 10
            """, (today,source))
        
            rows = state.cursor.fetchall()
        results = [
            {
                "title": r[0],
                "summary": r[1],
                "url": r[2]
            }
            for r in rows
        ]
        return results[:10]
    except Exception as e:
        print("[TOOL ERROR]", e)
        return [{"error": str(e)}]
