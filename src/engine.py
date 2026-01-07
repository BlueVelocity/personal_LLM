from typing import Iterator
import ollama
import threading
from datetime import date


class AIEngine:
    def __init__(self, model: str, search_term_model: str, router_model: str) -> None:
        self.model = model
        self.search_term_model = search_term_model
        self.router_model = router_model
        self.engine_options = {"num_ctx": 16384}
        self.models = self.get_models()
        self.client = ollama.Client()
        self.messages = []

        self.load_into_memory()

    def load_into_memory(self):
        thread = threading.Thread(
            target=self.client.generate,
            kwargs={
                "model": self.model,
                "options": self.engine_options,
                "keep_alive": 60,
            },
            daemon=True,
        )

        thread.start()

    def get_models(self) -> ollama.ListResponse:
        try:
            models = ollama.list()

            model_names = [m.model for m in models.models]

            has_main = self.model in model_names
            has_sub = self.search_term_model in model_names

            hint = "\nIs it configured correctly in config.yaml?\nHint: Run 'ollama list' to list installed models"
            if not has_main and not has_sub and self.model != self.search_term_model:
                raise Exception(
                    f"Model '{self.model}' and sub-model '{self.search_term_model}' are not installed.{hint}"
                )
            elif not has_main:
                raise Exception(f"Model '{self.model}' not installed.{hint}")
            elif not has_sub:
                raise Exception(
                    f"Sub-model '{self.search_term_model}' not installed.?{hint}"
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
        ollama.generate(model=self.search_term_model, keep_alive=0)

    # TODO: Add USER_DATA which will be passed in as an argument 'user_data' and added to the system message as 'USER_DATA:'
    def set_system_message(
        self, initial_context: str, initial_instructions: str, user_data: None
    ) -> None:
        self.messages.append(
            {
                "role": "system",
                "content": f"CONTEXT: {initial_context}\nCURRENT DATE: {date.today()}\nINSTRUCTIONS: {initial_instructions}",
            }
        )

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def add_search_message(self, content: str) -> None:
        self.messages.append(
            {"role": "user", "content": f"INTERNET SEARCH RESULTS:\n{content}"}
        )

    def get_response_stream(self) -> Iterator:
        stream = self.client.chat(
            model=self.model,
            messages=self.messages,
            options=self.engine_options,
            stream=True,
            keep_alive=60,
        )
        return stream
