import yaml
from pathlib import Path

from view import View
from engine import AIEngine
from search import SearchEngine
from cleanup_handler import register_cleanup


def get_config():
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"

    try:
        with open(f"{config_path}", "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at: {config_path}\n"
            "Have you created 'config.yaml' in the project root?"
        )


def main():
    config = get_config()
    model_name = config["model_info"]["MAIN_MODEL"]
    sub_model_name = config["model_info"]["SUB_MODEL"]
    initial_context = config["system_prompt"]["initial_context"]
    initial_instructions = config["system_prompt"]["system_instructions"]

    if sub_model_name == "" or sub_model_name is None:
        sub_model_name = model_name

    ai = AIEngine(model_name, sub_model_name)
    ai.set_system_message(initial_context, initial_instructions, user_data=None)
    ai.load()

    search_engine = SearchEngine(config["search_settings"]["engine_name"])

    view = View()

    view.print_header_panel(model_name, sub_model_name)

    def end_session():
        view.print("[bold red]Ending session...[/bold red]")
        ai.remove_from_memory()

    register_cleanup(end_session)

    try:
        while True:
            user_input = view.get_user_input()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                break

            ai.add_user_message(user_input)

            search_results = search_engine.text_query(user_input)
            ai.add_search_message(search_results)

            response_stream = ai.get_response_stream()

            ai_response = view.live_response(model_name, response_stream)

            try:
                ai.add_assistant_message(ai_response)
            except Exception as e:
                view.print(f"[bold red][!] Error:[/bold red] {e}")

    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
