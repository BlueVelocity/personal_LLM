import os
from dotenv import load_dotenv
from tavily import TavilyClient


class SearchEngine:
    def __init__(self, selected_engine) -> None:
        self.selected_engine = selected_engine

    def text_query(self, query: str) -> str:
        if self.selected_engine == "tavily":
            return self.search_tavily(query)
        else:
            return "Search Unsuccesful"

    def search_tavily(self, query: str) -> str:
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

            return context
        except Exception:
            raise Exception
