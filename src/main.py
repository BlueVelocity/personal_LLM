import tomllib
from pathlib import Path

from commands import handle_command
from models import ChatHeader
from view import View
from memory import Memory
from engine import AIEngine
from search import SearchEngine
from cleanup_handler import register_cleanup


def get_config():
    """Retrieves the config.toml from the root directory"""

    config_path = Path(__file__).resolve().parent.parent / "config.toml"

    try:
        with open(f"{config_path}", "rb") as file:
            return tomllib.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at: {config_path}\n"
            "Have you created 'config.toml' in the project root?"
        )


def main():
    config = get_config()

    main_model: str = config["models"]["MAIN"]
    search_term_model: str = config["models"]["SEARCH"]

    keep_alive: int = config["model_settings"]["keep_alive"]
    main_thinking: bool = config["model_settings"]["allow_main_thinking"]
    search_thinking: bool = config["model_settings"]["allow_search_thinking"]

    initial_context: str = config["system_prompt"]["initial_context"]
    initial_instructions: str = config["system_prompt"]["system_instructions"]

    search_engine: str = config["search_settings"]["engine_name"]
    search_headers: str = config["search_settings"]["headers"]

    if search_term_model == "" or search_term_model is None:
        search_term_model = main_model

    memory = Memory()

    ai = AIEngine(
        main_model,
        search_term_model,
        keep_alive=keep_alive,
        main_thinking=main_thinking,
        search_thinking=search_thinking,
    )
    ai.set_system_message(initial_context, initial_instructions, user_data=None)
    ai.load_into_memory()

    search = SearchEngine(search_engine, user_agent=search_headers)

    view = View()

    view.print_header_panel(main_model, search_term_model)

    view.print_system_message("Recent chats...")
    chat_list: list[ChatHeader] = memory.get_chat_list(5)
    view.print_ordered_list(
        [f"{chat.created}: {chat.title}" for chat in chat_list], descending=True
    )

    def end_session():
        view.print("[bold red][*] Ending session...[/bold red]")
        ai.remove_from_memory()

    register_cleanup(end_session)

    try:
        last_message_data: dict[str, str] = {"role": "", "message": ""}

        while True:
            user_input: str = view.get_user_input()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.lower().startswith("/"):
                handle_command(user_input, view, memory, ai)
                continue

            if not memory.current_id:
                words = user_input.split()
                truncated_message = " ".join(words[:10])
                memory.create_conversation(truncated_message)

            last_message_data = ai.add_user_message(user_input)
            memory.add_to_conversation(
                last_message_data["role"],
                last_message_data["content"],
                1,
            )

            notifications = []

            # Search the web
            view.print_system_message("Reviewing query...", True)
            search_decision = ai.determine_search()
            if search_decision["needs_search"]:
                view.print_system_message(
                    f"Searching the web for: [italic]{search_decision['search_term']}[/italic]..."
                )
                search_data = search.text_query(search_decision["search_term"])
                notifications: list[str] = search_data["notifications"]
                search_result: str = search_data["context"]

                last_message_data = ai.add_search_message(search_result)
                memory.add_to_conversation(
                    last_message_data["role"],
                    last_message_data["content"],
                    0,
                )
            else:
                view.print_system_message("Decided not to search.")

            # Get and print the response
            response_stream = ai.get_response_stream()
            ai_response = view.live_response(main_model, response_stream)

            last_message_data = ai.add_assistant_message(ai_response)
            memory.add_to_conversation(
                last_message_data["role"],
                last_message_data["content"],
                1,
            )

            view.print(notifications)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
