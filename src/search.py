import os
from typing import TypedDict
from dotenv import load_dotenv
from tavily import TavilyClient
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


class SearchResult(TypedDict):
    notifications: list[str]
    context: str


class SearchEngine:
    """Provides access to internet search engines"""

    def __init__(self, selected_engine: str, user_agent: str = "") -> None:
        self.selected_engine = selected_engine
        self.user_agent = user_agent

    def text_query(self, query: str) -> SearchResult:
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

    def search_tavily(self, query: str) -> SearchResult:
        """
        Searches the internet using Tavily
        Args:
            query: Search query
        """
        context: str = ""
        notifications: list[str] = []

        try:
            load_dotenv()

            tavily_client = TavilyClient(api_key=os.getenv("TAVILY_KEY"))
            response = tavily_client.search(query)

            for i, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "No Title")
                content = result.get("content", "")
                url = result.get("url", "")

                context += f"Source [{i}]: {title}\nURL: {url}\nContent: {content}\n\n"
                notifications.append(f"[{i}]: {url}")

            return {"notifications": notifications, "context": context}
        except Exception:
            raise Exception

    def search_duckduckgo(self, query: str) -> SearchResult:
        """
        Searches the internet using duckduckgo search
        Args:
            query: Search query
        """
        with DDGS() as ddgs:
            results: list[dict] = []
            notifications: list[str] = []
            context: str = ""

            for i, result in enumerate(
                ddgs.text(query, max_results=3, backend="duckduckgo")
            ):
                url = result.get("href")
                if url:
                    try:
                        headers = {"User-Agent": self.user_agent}
                        response = requests.get(url, headers=headers, timeout=10)
                        notifications.append(
                            f"[{response.status_code}]: {response.url}"
                        )
                        soup = BeautifulSoup(response.content, "html.parser")
                        text = soup.get_text(separator="\n", strip=True)
                        results.append(
                            {
                                "reference_num": f"[{i}]",
                                "title": result.get("title"),
                                "url": url,
                                "full_text": text,
                            }
                        )
                    except:
                        results.append(
                            {
                                "reference_num": f"[{i}]",
                                "title": result.get("title"),
                                "url": url,
                                "full_text": "Unable to fetch",
                            }
                        )

            for result in results:
                context += f"{result['reference_num']}: Title: {result['title']}\nURL: {result['url']}\n{result['full_text'][:5000]}...\n\n"

            return {"notifications": notifications, "context": context}
