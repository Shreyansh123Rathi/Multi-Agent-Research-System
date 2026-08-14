from langchain.tools import tool 
import requests #1.To fetch results from online
from bs4 import BeautifulSoup #2.web scrapping from the links
from tavily import TavilyClient #3.To take links online
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv() #4Import Kpis

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#1,Selecting links
@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=3)#a.save tokens, only 5

    out = []

    for r in results['results']:#b.Results mai bhi bahut si cheeze hoti h..like token etc..sirf links chaiye hai
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):#a.yeh sab ek web page k components hai
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
