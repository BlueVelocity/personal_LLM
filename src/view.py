from typing import Iterator
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML


class View:
    """Controls input and output as well as format for each to the console"""

    def __init__(self) -> None:
        self.CONSOLE = Console()
        self.history = InMemoryHistory()

    def print(self, message: str | list[str]) -> None:
        if type(message) is list:
            for i in message:
                self.CONSOLE.print(i)
        else:
            self.CONSOLE.print(message)

    def print_system_message(self, message: str | list[str], line_break: bool = False):
        def print_message(text: str | list[str]) -> None:
            match line_break:
                case True:
                    self.CONSOLE.print(f"\n[bold cyan][*][/bold cyan] {text}")
                case _:
                    self.CONSOLE.print(f"[bold cyan][*][/bold cyan] {text}")

        if type(message) is list:
            for m in message:
                print_message(m)
        else:
            print_message(message)

    def print_header_panel(self, model: str, search_model: str) -> None:
        self.CONSOLE.print(
            Panel(
                f"[bold yellow]Chat Session Started[/bold yellow]\n[bold cyan]Model: {model}[/bold cyan]\n[cyan]Search Model: {search_model}[/cyan]\n[yellow]Type 'exit' or 'quit' to end the session.[/yellow]",
                expand=True,
                border_style="yellow",
            ),
        )

    def get_user_input(self) -> str:
        try:

            def prompt_continuation(width, line_number, is_soft_wrap):
                return "." * (width - 1) + " "

            user_input = prompt(
                HTML("<ansiblue><b>\n> You:</b></ansiblue> "),
                multiline=True,
                prompt_continuation=prompt_continuation,
                history=self.history,
            ).strip()

            return user_input
        except Exception:
            raise Exception

    def live_response(self, model_name: str, response_stream: Iterator):
        full_response = ""
        with Live(
            Panel(
                "Thinking...",
                title=f"[bold cyan]{model_name}[/bold cyan]",
                title_align="left",
                border_style="cyan",
                expand=True,
            ),
            console=self.CONSOLE,
            refresh_per_second=50,
        ) as live:
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
        return full_response
