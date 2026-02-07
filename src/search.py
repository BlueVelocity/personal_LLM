import os
from typing import TypedDict
from dotenv import load_dotenv
from tavily import TavilyClient
import httpx
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import trafilatura


class SearchResult(TypedDict):
    notifications: list[str]
    context: str
    message: str


class SearchEngine:
    """Provides access to internet search engines"""

    def __init__(
        self,
        selected_engine: str,
        user_agent: str = "",
        use_tor: bool = True,
        tor_port: int = 9050,
    ) -> None:
        self.selected_engine = selected_engine
        self.user_agent = user_agent
        self.use_tor = use_tor
        self.tor_port = tor_port

    def text_query(self, query: str) -> SearchResult:
        """
        Searches the internet using the selected search tool

        Args:
            query: Search query

        Returns:
            Dictionary with 'notifications' and 'context' keys
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

        Returns:
            Dictionary with 'notifications' and 'context' keys
        """
        context: str = ""
        notifications: list[str] = []
        message = ""

        try:
            load_dotenv()
            api_key = os.getenv("TAVILY_KEY")

            if not api_key:
                raise ValueError("TAVILY_KEY not found in environment variables")

            tavily_client = TavilyClient(api_key=api_key)
            response = tavily_client.search(query)

            for i, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "No Title")
                content = result.get("content", "")
                url = result.get("url", "")

                context += (
                    f"REFERENCE_NUM: [{i}]\n"
                    f"TITLE: {title}\n"
                    f"URL: {url}\n"
                    f"CONTENT: {content}\n\n"
                )
                notifications.append(f"Fetched: {url}")

            return {
                "notifications": notifications,
                "context": context,
                "message": message,
            }

        except ValueError as e:
            notifications.append(f"Configuration error: {str(e)}")
            return {"notifications": notifications, "context": "", "message": message}

        except Exception as e:
            notifications.append(f"Tavily search error: {str(e)}")
            return {"notifications": notifications, "context": "", "message": message}

    def search_duckduckgo(self, query: str) -> SearchResult:
        """
        Searches the internet using duckduckgo search with article-focused content extraction.

        Args:
            query: Search query

        Returns:
            Dictionary with 'notifications' and 'context' keys
        """
        message: str = ""

        if self.use_tor:
            TOR_PROXY = f"socks5://127.0.0.1:{self.tor_port}"
            try:
                with httpx.Client(proxy=TOR_PROXY) as check_client:
                    response = check_client.get("https://check.torproject.org/api/ip")
                    message += f"Tor Verified: {response.text}"
            except httpx.ConnectError as e:
                raise e
        else:
            TOR_PROXY = ""

        with DDGS(proxy=TOR_PROXY) as ddgs:
            results: list[dict] = []
            notifications: list[str] = []
            context: str = ""

            search_results = ddgs.text(query, max_results=5, backend="duckduckgo")

            for i, result in enumerate(search_results):
                url = result.get("href")
                if url:
                    try:
                        headers = {"User-Agent": self.user_agent}
                        response = requests.get(url, headers=headers, timeout=2)
                        notifications.append(
                            f"[{response.status_code}]: {response.url}"
                        )

                        extracted_text = trafilatura.extract(
                            response.content,
                            include_comments=False,
                            include_tables=True,
                            no_fallback=False,
                        )

                        if not extracted_text:
                            soup = BeautifulSoup(response.content, "html.parser")

                            # Remove unwanted elements
                            for element in soup(
                                [
                                    "script",
                                    "style",
                                    "nav",
                                    "footer",
                                    "header",
                                    "aside",
                                ]
                            ):
                                element.decompose()

                            # Try to find main content areas
                            main_content = (
                                soup.find("main")
                                or soup.find("article")
                                or soup.find(
                                    "div",
                                    class_=[
                                        "content",
                                        "main-content",
                                        "post-content",
                                    ],
                                )
                                or soup.body
                            )
                            extracted_text = (
                                main_content.get_text(separator="\n", strip=True)
                                if main_content
                                else ""
                            )

                        # Clean up the text
                        cleaned_text = "\n".join(
                            line.strip()
                            for line in extracted_text.split("\n")
                            if line.strip()
                        )

                        # Truncate to reasonable length (keeping slightly more for context)
                        truncated_text = cleaned_text[:2000]

                        results.append(
                            {
                                "reference_num": f"[{i + 1}]",
                                "title": result.get("title"),
                                "url": url,
                                "text": truncated_text,
                            }
                        )

                    except requests.RequestException as e:
                        notifications.append(f"Request error for {url}: {str(e)}")
                        results.append(
                            {
                                "reference_num": f"[{i + 1}]",
                                "title": result.get("title"),
                                "url": url,
                                "text": "Unable to fetch - request failed",
                            }
                        )
                    except Exception as e:
                        notifications.append(f"Error processing {url}: {str(e)}")
                        results.append(
                            {
                                "reference_num": f"[{i + 1}]",
                                "title": result.get("title"),
                                "url": url,
                                "text": "Unable to process content",
                            }
                        )

            # Build context string
            for result in results:
                context += (
                    f"REFERENCE_NUM: {result['reference_num']}\n"
                    f"TITLE: {result['title']}\n"
                    f"URL: {result['url']}\n"
                    f"CONTENT: {result['text']}...\n\n"
                )

            return {
                "notifications": notifications,
                "context": context,
                "message": message,
            }
