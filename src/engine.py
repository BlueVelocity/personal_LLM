from typing import Iterator
import ollama
import threading
from datetime import date
import copy
import json


class AIEngine:
    """Provides connection with model and moderates interaction"""

    def __init__(self, model: str, search_model: str, time_limit: int) -> None:
        self.model = model
        self.search_model = search_model
        self.time_limit = time_limit
        self.engine_options = {"num_ctx": 16384}
        self.models = self.get_models()
        self.client = ollama.Client()
        self.messages = []

        self.load_into_memory()

    def load_into_memory(self) -> None:
        """Loads the model(s) into memory on running the program"""
        thread = threading.Thread(
            target=self.client.generate,
            kwargs={
                "model": self.model,
                "options": self.engine_options,
                "keep_alive": self.time_limit,
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
                    "keep_alive": self.time_limit,
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

            hint = "\nIs it configured correctly in config.yaml?\nHint: Run 'ollama list' to list installed models"
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

    def add_user_message(self, content: str) -> dict[str, str]:
        """
        Adds a user message to the message log

        Args:
            content: Content to add to user message

        Returns:
            Dictionary with message role and content
        """
        message_info = {"role": "user", "content": content}

        self.messages.append(message_info)

        return message_info

    def add_assistant_message(self, content: str) -> dict[str, str]:
        """
        Adds an assistant message to the message log

        Args:
            content: Content to add to assistant message

        Returns:
            Dictionary with message role and content
        """
        message_info = {"role": "assistant", "content": content}

        self.messages.append(message_info)

        return message_info

    def add_search_message(self, content: str) -> dict[str, str]:
        """
        Adds a search message to the message log

        Args:
            content: Content to add to the search message

        Returns:
            Dictionary with message role and content
        """
        message_info = {
            "role": "user",
            "content": f"INTERNET SEARCH RESULTS:\n{content}",
        }

        self.messages.append(message_info)

        return message_info

    def get_response_stream(self) -> Iterator:
        """Returns the Ollama model response stream"""

        stream = self.client.chat(
            model=self.model,
            messages=self.messages,
            options=self.engine_options,
            stream=True,
            keep_alive=self.time_limit,
        )
        return stream

    def determine_search(self) -> dict[str, str]:
        """Determines if search is required given the current chat context"""
        copy_of_messages = copy.deepcopy(self.messages)

        copy_of_messages[0] = {
            "role": "system",
            "content": f"""CONTEXT: You are an AI working for another AI assistant to determine if they need to do an internet search to best serve the user.
            CURRENT DATE: {date.today()}.
            INSTRUCTIONS: 
            Only search the internet if it is needed for extra context.
            Search the internet if explicitly asked (i.e. "look it up...", "google...", "search...", etc.)
            If you do not know, or the information is not available, look it up on the internet.
            Be sure to include the date in the request if required.
            Review conversation history and responses, and analyze the LATEST QUERY. Does it require a new real-time web search?
            Respond ONLY in JSON format. Respond: {{"needs_search": true, "search_term": "..."}} or {{"needs_search": false, "search_term": ""}}
            """,
        }

        copy_of_messages[-1] = {
            "role": "user",
            "content": f"""
            LATEST_QUERY:
            {self.messages[-1]}
            """,
        }

        response = self.client.chat(
            model=self.search_model,
            messages=copy_of_messages,
            format="json",
            options=self.engine_options,
            stream=False,
        )

        result = json.loads(response["message"]["content"])

        return {
            "needs_search": result.get("needs_search"),
            "search_term": result.get("search_term"),
        }
