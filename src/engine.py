from typing import Iterator
import ollama
import threading
from datetime import date
import copy
import json

from models import UserData


class AIEngine:
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

    def no_thinking_main_fallback(self) -> None:
        self.main_thinking = False
        self.load_into_memory()

    def get_models(self) -> ollama.ListResponse:
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
        ollama.generate(model=self.model, keep_alive=0)
        ollama.generate(model=self.search_model, keep_alive=0)

    def get_response_stream(self, messages: list[dict[str, str]]) -> Iterator:
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
        copy_of_messages = copy.deepcopy(messages)

        copy_of_messages[0] = {
            "role": "system",
            "content": "You are a search intent classifier. Output only valid JSON.",
        }

        copy_of_messages[-1] = {
            "role": "user",
            "content": f"""
            CURRENT DATE: {date.today()}.

            USER DATA: {user_data}

            Decision Logic:
            - SEARCH (true) if: Query requires current dates, real-time events, specific facts (CEOs, prices, news), or you don't know or are unsure of something that is important in context. ALWAYS search if the user requests a search or for you to look it up.
            - NO SEARCH (false) if: Query is about logic, math, general concepts, coding syntax, historical well-known facts, or creative writing.

            Optimization Rules:
            1. Context: Include the full date if the query is time-sensitive. Include other information as necessary.

            Output Format (JSON ONLY):
            {{"needs_search": bool, "search_term": "string"}}

            LATEST_QUERY:
            {messages[-1]}
            """,
        }

        try:
            response = self.client.chat(
                model=self.search_model,
                messages=copy_of_messages,
                format="json",
                options=self.engine_options,
                stream=False,
                think=self.search_thinking,
            )
        except ollama.ResponseError:
            self.search_thinking = False

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
