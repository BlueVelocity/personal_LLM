import ollama
from schemas import Message


class AIEngine:
    def __init__(self, model) -> None:
        self.model = model
        self.models = self.get_models()
        self.client = ollama.Client()

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

    def remove_from_memory(self):
        ollama.generate(model=self.model, keep_alive=0)

    def get_response_stream(self, messages: list[Message]):
        stream = self.client.chat(
            model=self.model,
            messages=messages,
            options={"num_ctx": 16384},
            stream=True,
            keep_alive=60,
        )
        return stream
