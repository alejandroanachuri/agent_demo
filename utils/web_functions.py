import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
from urllib.parse import urljoin

def open_page(url:str) -> str:
    """
    Abre una pagina web y retorna el contenido en html y genera una lista de links a notas
    contenidas en el diario.
    """
    print('Open page: ', url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }   
    html = requests.get(url, headers=headers).text
    return html[:900000]

def extract_links(base_url, html):
    """
    Extrae los links de un contenido html, donde interesan los links a las noticias.
    """
    print("Extracting links...........")
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        link = a["href"]
        full_url = urljoin(base_url, link)
        links.append({
            "text": a.get_text(strip=True),
            "href": full_url
        })
    links = filter_articles(links)    
    return links[:20]


def filter_articles(articles):
    filtered = []
    for article in articles:
        title = article.get("text", "").strip()
        if len(title) >= 20:
            filtered.append(article)
    return filtered

def build_news_index(base_url):
    html = open_page(base_url)
    links = extract_links(base_url, html)
    print("Generating index...")
    index = []
    for link in links:
        summary = extract_summary(link["href"], link["text"])
        index.append({
            "title": link["text"],
            "summary":summary,
            "url": link["href"]
        })
    return index

def extract_summary(url, title):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # 1️⃣ meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"][:200]

        # 2️⃣ primer párrafo
        p = soup.find("p")
        if p:
            text = p.get_text(strip=True)
            if len(text) > 50:
                return text[:200]

    except Exception as e:
        print("summary error:", e)

    # 3️⃣ fallback
    return title