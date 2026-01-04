import yaml
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from datetime import date
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML

from engine import AIEngine
from schemas import Message


def get_config():
    absolute_path = Path(__file__).resolve()

    with open(f"{absolute_path.parent.parent}/config.yaml", "r") as file:
        return yaml.safe_load(file)


# TODO: Add USER_DATA which will be passed in as an argument 'user_data' and added to the system message as 'USER_DATA:'
def initialize_messages(initial_context, initial_instructions) -> list[Message]:
    system_message: Message = {
        "role": "system",
        "content": f"""
        CONTEXT: {initial_context}
        CURRENT DATE: {date.today()}.
        INSTRUCTIONS: {initial_instructions} 
        """,
    }
    return [system_message]


def main():
    CONSOLE = Console()

    config = get_config()
    model_name = config["model_info"]["MAIN_MODEL"]
    sub_model_name = config["model_info"]["SUB_MODEL"]

    messages = initialize_messages(
        config["system_prompt"]["initial_context"],
        config["system_prompt"]["system_instructions"],
    )
    ai = AIEngine(model_name)

    CONSOLE.print(
        Panel(
            f"[bold yellow]Chat Session Started[/bold yellow]\n[bold cyan]Model: {model_name}[/bold cyan]\n[cyan]Sub Model: {sub_model_name}[/cyan]\n[yellow]Type 'exit' or 'quit' to end the session.[/yellow]",
            expand=True,
            border_style="yellow",
        ),
    )

    while True:
        try:
            # This function adds "..." to the start of new lines
            def prompt_continuation(width, line_number, is_soft_wrap):
                return "." * (width - 1) + " "

            user_input = prompt(
                HTML("<ansiblue><b>\n> You:</b></ansiblue> "),
                multiline=True,
                prompt_continuation=prompt_continuation,
            ).strip()

            if not user_input:
                continue
        except EOFError:
            break

        if user_input.lower() in ["exit", "quit"]:
            CONSOLE.print("[bold red]Ending session...[/bold red]")
            break

        # Add User Message to History
        messages.append({"role": "user", "content": user_input})

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
                response_stream = ai.get_response_stream(messages)

                for chunk in response_stream:
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
            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            CONSOLE.print(f"[bold red][!] Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
