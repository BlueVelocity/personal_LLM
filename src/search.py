import os
from dotenv import load_dotenv
from tavily import TavilyClient
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


class SearchEngine:
    """Provides access to internet search engines"""

    def __init__(self, selected_engine: str, user_agent: str = "") -> None:
        self.selected_engine = selected_engine
        self.user_agent = user_agent

    def text_query(self, query: str) -> str:
        """
        Searches the internet using the selected search tool
        Args:
            query: Search query
        """
        match self.selected_engine:
            case "tavily":
                return self.search_tavily(query)
            case "ddgs":
                return self.search_duckduckgo(query)
            case _:
                raise Exception("No engine selected, search unsuccesful")

    def search_tavily(self, query: str) -> str:
        """
        Searches the internet using Tavily
        Args:
            query: Search query
        """
        context = ""
        try:
            load_dotenv()

            tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
            response = tavily_client.search(query)

            for i, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "No Title")
                content = result.get("content", "")
                url = result.get("url", "")

                context += f"Source [{i}]: {title}\nURL: {url}\nContent: {content}\n\n"
                print(f"[{i}]: {url}")

            return context
        except Exception:
            raise Exception

    def search_duckduckgo(self, query: str) -> str:
        """
        Searches the internet using duckduckgo search
        Args:
            query: Search query
        """
        with DDGS() as ddgs:
            results = []

            for r in ddgs.text(query, max_results=3, backend="duckduckgo"):
                url = r.get("href")
                if url:
                    try:
                        headers = {"User-Agent": self.user_agent}
                        response = requests.get(url, headers=headers, timeout=10)
                        print(f"[{response.status_code}]: {response.url}")
                        soup = BeautifulSoup(response.content, "html.parser")
                        text = soup.get_text(separator="\n", strip=True)
                        results.append(
                            {"title": r.get("title"), "url": url, "full_text": text}
                        )
                    except:
                        results.append(
                            {
                                "title": r.get("title"),
                                "url": url,
                                "full_text": "Unable to fetch",
                            }
                        )

            context = ""
            for result in results:
                context += f"Title: {result['title']}\nURL: {result['url']}\n{result['full_text'][:5000]}...\n\n"
            return context
