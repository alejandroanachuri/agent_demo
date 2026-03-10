import requests
from bs4 import BeautifulSoup
from agents import function_tool
from newspaper import Article, Config
from urllib.parse import urljoin
from utils import state

@function_tool
def search_news_que_pasa_jujuy(topic: str) -> list:
    """
    Busca noticias en el indice actual del diario que pasa jujuy.
    """
    print('Searching local index in Que Pasa Jujuy..')
    results = []
    for article in state.que_pasa_jujuy_index:
        if topic.lower() in article["title"].lower():
            results.append(article)
    if not results:
        return state.que_pasa_jujuy_index
    return results[:10]

@function_tool
def search_news_infobae(topic: str) -> list:
    """
    Busca noticias en el indice actual del diario Infobae con noticias nacionales.
    """
    print('Searching local index in Infobae..')
    results = []
    for article in state.infobae_index:
        if topic.lower() in article["title"].lower():
            results.append(article)
    if not results:
        return state.infobae_index
    return results[:10]

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

