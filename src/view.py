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

    def print(self, message: str | list[str], line_break: bool = False) -> None:
        if line_break:
            self.CONSOLE.print("\n")

        if type(message) is list:
            for i in message:
                self.CONSOLE.print(i)
        else:
            self.CONSOLE.print(message)

    def print_system_message(self, message: str | list[str], line_break: bool = False):
        if type(message) is list:
            self.print([f"[bold cyan][*][/bold cyan] {m}" for m in message], line_break)
        else:
            self.print([f"[bold cyan][*][/bold cyan] {message}"])

    def print_ordered_list(
        self,
        message_list: list[str],
        line_break: bool = False,
        descending: bool = False,
    ):
        if descending:
            for i, message in enumerate(message_list):
                self.print(
                    [f"[bold cyan][{len(message_list) - 1 - i}][/bold cyan] {message}"],
                    line_break,
                )
        else:
            for i, message in enumerate(message_list):
                self.print([f"[bold cyan][{i}][/bold cyan] {message}"], line_break)

    def print_header_panel(self, model: str, search_model: str) -> None:
        self.CONSOLE.print(
            Panel(
                f"[bold yellow]Chat Session Started[/bold yellow]\n[yellow]Type 'exit' or 'quit' to end the session.[/yellow]\n[bold yellow]Model:[/bold yellow] [bold cyan]{model}[/bold cyan]\n[bold yellow]Search Model:[/bold yellow] [cyan]{search_model}[/cyan]",
                expand=True,
                border_style="yellow",
            ),
        )

    def print_user_message(self, message: str):
        self.CONSOLE.print(f"\n[bold blue]> You:[/bold blue] {message}\n")

    def print_assistant_message(self, message: str, name: str):
        self.CONSOLE.print(
            Panel(
                Markdown(message),
                title=f"[bold cyan]{name}[/bold cyan]",
                title_align="left",
                border_style="cyan",
                expand=True,
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
