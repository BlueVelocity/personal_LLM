import tomllib
from pathlib import Path
from typing import Any

from commands import handle_command
from models import ChatHeader
from view import View
from memory import Memory
from engine import AIEngine
from search import SearchEngine
from cleanup_handler import register_cleanup
from models import ModelConfig, SearchConfig, StyleConfig


def get_config():
    """Retrieves the config.toml from the root directory"""

    config_path = Path(__file__).resolve().parent.parent / "config.toml"

    try:
        with open(f"{config_path}", "rb") as file:
            return parse_config(tomllib.load(file))
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at: {config_path}\n"
            "Have you created 'config.toml' in the project root?"
        )


def parse_config(
    config_data: dict[str, Any],
) -> tuple[ModelConfig, SearchConfig, StyleConfig]:
    """Parses the config and sorts into descriptive objects"""

    if (
        config_data["model_settings"]["search_model"] == ""
        or config_data["model_settings"]["main_model"] is None
    ):
        config_data["model_settings"]["search_model"] = config_data["model_settings"][
            "main_model"
        ]

    model_config: ModelConfig = ModelConfig(**config_data["model_settings"])
    search_config: SearchConfig = SearchConfig(**config_data["search_settings"])
    style_config: StyleConfig = StyleConfig(**config_data["style_settings"])

    return (model_config, search_config, style_config)


def main():
    model_config, search_config, style_config = get_config()

    memory = Memory()

    ai = AIEngine(
        model_config.main_model,
        model_config.search_model,
        keep_alive=model_config.keep_alive,
        main_thinking=model_config.main_thinking,
        search_thinking=model_config.search_thinking,
    )
    ai.load_into_memory()

    search = SearchEngine(
        search_config.search_engine, user_agent=search_config.search_headers
    )

    view = View()
    view.print_panel(
        f"[bold {style_config.header}]Chat Session Started[/bold {style_config.header}][{style_config.header}]\n > 'Enter': Submit query.\n > 'Alt + Enter': New line.\nType '/help' for a list of commands.[/{style_config.header}]",
        style=style_config.header,
    )

    # Print history
    chat_list: list[ChatHeader] = memory.get_chat_list(3)
    view.print_table(
        "Chat History",
        ["ID", "Last Updated", "Title"],
        chat_list,
        col_alignment=["center", "center", "left"],
        expand=True,
        style=style_config.system,
    )

    def end_session():
        """Notifies the user the session is ending and unloads the llm from memory"""
        view.print_system_message(
            "Ending session...", style=style_config.warning, line_break=True
        )
        ai.remove_from_memory()

    register_cleanup(end_session)

    try:
        while True:
            user_input: str = view.get_user_input()
            if not user_input:
                continue

            if user_input.lower() == "/exit":
                break

            if user_input.lower().startswith("/"):
                handle_command(user_input, view, memory, ai, style=style_config.system)
                continue

            if not memory.current_id:
                words = user_input.split()
                truncated_message = " ".join(words[:10])
                memory.create_conversation(truncated_message)
                memory.add_system_message(
                    model_config.initial_context, model_config.system_instructions
                )

            memory.add_user_message(user_input)

            notifications = []

            # Search the web
            view.print_system_message(
                "Reviewing query...", style=style_config.system, line_break=True
            )
            search_decision = ai.determine_search(
                memory.get_llm_formatted_chat_history()
            )
            if search_decision["needs_search"]:
                view.print_system_message(
                    f"Searching the web for: [italic]{search_decision['search_term']}[/italic]...",
                    style=style_config.system,
                )
                search_data = search.text_query(search_decision["search_term"])
                notifications: list[str] = search_data["notifications"]
                search_result: str = search_data["context"]

                memory.add_search_message(search_result)
            else:
                view.print_system_message(
                    "Decided not to search.", style=style_config.system
                )

            # Get and print the response
            response_stream = ai.get_response_stream(
                memory.get_llm_formatted_chat_history()
            )
            ai_response = view.live_response(
                model_config.main_model, response_stream, style=style_config.assistant
            )

            memory.add_assistant_message(ai_response)

            if notifications:
                view.print_system_message("Search sources:", style=style_config.system)
                view.print_ordered_list(notifications, style=style_config.system)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
