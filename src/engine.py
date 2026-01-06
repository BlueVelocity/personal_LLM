import ollama
import threading
from datetime import date


class AIEngine:
    def __init__(self, model) -> None:
        self.model = model
        self.engine_options = {"num_ctx": 16384}
        self.models = self.get_models()
        self.client = ollama.Client()
        self.messages = []

        self.load()

    def load(self):
        thread = threading.Thread(
            target=self.client.generate,
            kwargs={
                "model": self.model,
                "options": self.engine_options,
                "keep_alive": 60,
            },
            daemon=True,
        )
        thread.start()  # Starts the thread and returns immediately

    def get_models(self):
        try:
            models = ollama.list()
        except ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama. Is the service running?"
            )

        except ollama.ResponseError:
            raise

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        else:
            return models

    def remove_from_memory(self) -> None:
        ollama.generate(model=self.model, keep_alive=0)

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

    def add_user_message(self, content) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def get_response_stream(self):
        stream = self.client.chat(
            model=self.model,
            messages=self.messages,
            options=self.engine_options,
            stream=True,
            keep_alive=60,
        )
        return stream
