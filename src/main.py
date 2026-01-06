import yaml
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML

from engine import AIEngine


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
    CONSOLE = Console()
    chat_history_log = InMemoryHistory()

    def end_session():
        CONSOLE.print("[bold red]Ending session...[/bold red]")
        ai.remove_from_memory()

    config = get_config()
    model_name = config["model_info"]["MAIN_MODEL"]
    sub_model_name = config["model_info"]["SUB_MODEL"]

    initial_context = config["system_prompt"]["initial_context"]
    initial_instructions = config["system_prompt"]["system_instructions"]

    ai = AIEngine(model_name)
    ai.set_system_message(initial_context, initial_instructions, user_data=None)
    ai.load()

    CONSOLE.print(
        Panel(
            f"[bold yellow]Chat Session Started[/bold yellow]\n[bold cyan]Model: {model_name}[/bold cyan]\n[cyan]Sub Model: {sub_model_name}[/cyan]\n[yellow]Type 'exit' or 'quit' to end the session.[/yellow]",
            expand=True,
            border_style="yellow",
        ),
    )

    try:
        while True:
            try:
                # This function adds "..." to the start of new lines
                def prompt_continuation(width, line_number, is_soft_wrap):
                    return "." * (width - 1) + " "

                user_input = prompt(
                    HTML("<ansiblue><b>\n> You:</b></ansiblue> "),
                    multiline=True,
                    prompt_continuation=prompt_continuation,
                    history=chat_history_log,
                ).strip()

                if not user_input:
                    continue
            except EOFError:
                break

            if user_input.lower() in ["exit", "quit"]:
                end_session()
                break

            # Add User Message to History
            ai.add_user_message(user_input)

            full_response = ""

            try:
                print("")
                with Live(
                    Panel(
                        "Thinking...",
                        title=f"[bold cyan]{model_name}[/bold cyan]",
                        title_align="left",
                        border_style="cyan",
                        expand=True,
                    ),
                    console=CONSOLE,
                    refresh_per_second=50,
                ) as live:
                    for chunk in ai.get_response_stream():
                        content = chunk["message"]["content"]
                        if content:
                            full_response += content
                            live.update(
                                Panel(
                                    Markdown(full_response),
                                    title=f"[bold cyan]{model_name}[/bold cyan]",
                                    title_align="left",
                                    border_style="cyan",
                                    expand=True,
                                )
                            )

                # Save AI response to history
                ai.add_assistant_message(full_response)

            except Exception as e:
                CONSOLE.print(f"[bold red][!] Error:[/bold red] {e}")
    except KeyboardInterrupt:
        end_session()


if __name__ == "__main__":
    main()
