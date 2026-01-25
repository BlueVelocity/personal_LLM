from typing import Iterator
import ollama
import threading
from datetime import date
import copy
import json

from models import UserData


class AIEngine:
    """Provides connection with model and moderates interaction"""

    def __init__(
        self,
        model: str,
        search_model: str,
        keep_alive: int,
        main_thinking: bool,
        search_thinking: bool,
    ) -> None:
        self.model = model
        self.search_model = search_model

        self.keep_alive = keep_alive
        self.main_thinking = main_thinking
        self.search_thinking = search_thinking

        self.engine_options = {"num_ctx": 16384}
        self.models = self.get_models()
        self.client = ollama.Client()

        self.load_into_memory()

    def load_into_memory(self) -> None:
        """Loads the model(s) into memory on running the program"""
        thread = threading.Thread(
            target=self.client.generate,
            kwargs={
                "model": self.model,
                "options": self.engine_options,
                "keep_alive": self.keep_alive,
            },
            daemon=True,
        )

        thread.start()

        if self.model != self.search_model:
            search_thread = threading.Thread(
                target=self.client.generate,
                kwargs={
                    "model": self.search_model,
                    "options": self.engine_options,
                    "keep_alive": self.keep_alive,
                },
                daemon=True,
            )

            search_thread.start()

    def get_models(self) -> ollama.ListResponse:
        """Gets the model list and checks that Ollama is running and aavailable"""
        try:
            models = ollama.list()

            model_names = [m.model for m in models.models]

            has_main = self.model in model_names
            has_search = self.search_model in model_names

            hint = "\nIs it configured correctly in config.toml?\nHint: Run 'ollama list' to list installed models"
            if not has_main and not has_search and self.model != self.search_model:
                raise Exception(
                    f"Model '{self.model}' and sub-model '{self.search_model}' are not installed.{hint}"
                )
            elif not has_main:
                raise Exception(f"Model '{self.model}' not installed.{hint}")
            elif not has_search:
                raise Exception(
                    f"Search-model '{self.search_model}' not installed.?{hint}"
                )

        except ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama.\nIs the service running?"
            )

        except ollama.ResponseError:
            raise

        else:
            return models

    def remove_from_memory(self) -> None:
        """Clears the model(s) from RAM"""
        ollama.generate(model=self.model, keep_alive=0)
        ollama.generate(model=self.search_model, keep_alive=0)

    def get_response_stream(self, messages: list[dict[str, str]]) -> Iterator:
        """Returns the Ollama model response stream"""

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            options=self.engine_options,
            stream=True,
            keep_alive=self.keep_alive,
            think=self.main_thinking,
        )
        return stream

    def determine_search(
        self, messages: list[dict[str, str]], user_data: UserData
    ) -> dict[str, str]:
        """Determines if search is required given the current chat context"""
        copy_of_messages = copy.deepcopy(messages)

        copy_of_messages[0] = {
            "role": "system",
            "content": f"""
            CONTEXT: You are an AI working for another AI assistant to determine if they need to do an internet search to best serve the user.
            CURRENT DATE: {date.today()}.

            INSTRUCTIONS: Review the conversation history and analyze the LATEST QUERY to determine if it requires a real-time web search. Search the internet when: (1) explicitly asked by the user (e.g., "look it up," "google," "search"), (2) the information needed is not reliably known or available, (3) the query involves current events, recent developments, or time-sensitive information that may have changed, or (4) verification of current facts, positions, or status is needed (e.g., "who is the current CEO," "what's the latest policy"). When searching is needed, create clear, specific search queries using natural language that matches how people actually search—keep them concise (1-6 words when possible), focus on the core intent, and include relevant context like dates when required. Prefer targeted phrases over single words: instead of "weather," use "weather forecast [city] today." Start broad with short queries, then add detail if needed to narrow results.

            When searching is NOT needed: Do not search for timeless information, fundamental concepts, well-established facts, or queries you can answer reliably from existing knowledge. For example, never search for basic definitions, historical dates, simple coding questions, or conceptual explanations that won't have changed.

            Respond ONLY in JSON format: {{"needs_search": true, "search_term": "..."}} or {{"needs_search": false, "search_term": ""}}
            USER DATA: {user_data}
            """,
        }

        copy_of_messages[-1] = {
            "role": "user",
            "content": f"""
            LATEST_QUERY:
            {messages[-1]}
            """,
        }

        response = self.client.chat(
            model=self.search_model,
            messages=copy_of_messages,
            format="json",
            options=self.engine_options,
            stream=False,
            think=self.search_thinking,
        )

        result = json.loads(response["message"]["content"])

        return {
            "needs_search": result.get("needs_search"),
            "search_term": result.get("search_term"),
        }
