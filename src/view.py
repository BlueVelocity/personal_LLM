from sys import thread_info
from typing import Iterator, Iterable, NamedTuple
from ollama import ResponseError
from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

from models import ChatItem, ModelResponse


class View:
    """Controls input and output as well as format for each to the console"""

    def __init__(self) -> None:
        self.CONSOLE = Console(highlight=False)
        self.history = InMemoryHistory()

    def print(self, message: str | list[str], line_break: bool = False) -> None:
        if line_break:
            self.CONSOLE.print("")

        self.CONSOLE.print(message)

    def print_system_message(self, message: str, style: str, line_break: bool = False):
        self.print(
            f"[bold {style}][*][/bold {style}][{style}] {message}[/{style}]", line_break
        )

    def print_ordered_list(
        self,
        message_list: list[str],
        style: str,
        line_break: bool = False,
    ):
        for i, message in enumerate(message_list):
            self.print(
                f"[bold {style}][{i + 1}][/bold {style}][{style}] {message}[/{style}]",
                line_break,
            )

    def print_unordered_list(
        self,
        message_list: list[str],
        style: str,
        line_break: bool = False,
    ):
        for message in message_list:
            self.print(
                f"[bold {style}] > [/bold {style}][{style}] {message}[{style}]",
                line_break,
            )

    def print_table(
        self,
        title: str,
        columns: list,
        rows: Iterable[Iterable[str]],
        style: str,
        line_break=False,
        col_alignment: list[str] | None = None,
        expand: bool = False,
    ) -> None:
        if line_break:
            self.print("\n")

        table = Table(
            title=title,
            style=style,
            title_style=style + " bold italic",
            header_style=style + " bold",
            expand=expand,
            box=box.ROUNDED,
        )

        for i, column_header in enumerate(columns):
            alignment = "center"

            if col_alignment and col_alignment[i] in ["left", "center", "right"]:
                alignment = col_alignment[i]

            if i == len(columns) - 1:
                ratio = 1
            else:
                ratio = None

            table.add_column(
                column_header,
                justify=alignment,
                style=style,
                no_wrap=True,
                ratio=ratio,
            )

        for data in rows:
            str_data = (str(item) for item in data)
            table.add_row(*str_data)

        self.CONSOLE.print(table)

    def print_panel(self, message: str, style: str) -> None:
        self.CONSOLE.print(
            Panel(
                message,
                expand=True,
                border_style=style,
            ),
        )

    def print_user_message(self, message: str, style: str):
        self.CONSOLE.print(f"\n[bold {style}] > You:[/bold {style}] {message}\n")

    def print_assistant_message(self, message: str, name: str, style: str):
        self.CONSOLE.print(
            Panel(
                Markdown(message),
                title=f"[bold {style}]{name}[/bold {style}]",
                title_align="left",
                border_style=style,
                expand=True,
            ),
        )

    def get_user_input(self) -> str:
        kb = KeyBindings()

        @kb.add(
            "enter"
        )  # Handles Enter key. Changes default from newline to submit query.
        def _(event):
            """Pressing Enter submits the message."""
            event.current_buffer.validate_and_handle()

        @kb.add(
            "escape", "enter"
        )  # Handles Alt + Enter keys or Esc then Enter keys. Is Escape followed by Enter.
        def _(event):
            """Pressing Alt+Enter inserts a new line."""
            event.current_buffer.insert_text("\n")

        def prompt_continuation(width, line_number, is_soft_wrap):
            return "." * (width - 1) + " "

        user_input = prompt(
            HTML("<ansiblue><b>\n > You:</b></ansiblue> "),
            multiline=True,
            key_bindings=kb,
            prompt_continuation=prompt_continuation,
            history=self.history,
        ).strip()

        return user_input

    def live_response(
        self,
        model_name: str,
        time: str,
        response_stream: Iterator,
        style: str,
        thinking_style,
    ):
        thinking_str: str = ""
        content_str: str = ""

        with Live(
            console=self.CONSOLE,
            refresh_per_second=12,
        ) as live:
            for chunk in response_stream:
                msg = chunk.get("message", {})
                thinking = msg.get("thinking")
                content = msg.get("content")

                if thinking:
                    thinking_str += thinking
                if content:
                    content_str += content

                # Create a display group to stack elements
                display_elements = []

                if thinking_str:
                    display_elements.append(
                        Panel(
                            Markdown(thinking_str),
                            title=f"{model_name}'s Thoughts...",
                            style=thinking_style,
                            border_style=thinking_style,
                            title_align="left",
                            expand=True,
                        )
                    )

                if content_str:
                    display_elements.append(
                        Panel(
                            Markdown(content_str),
                            title=f"[bold {style}]{model_name}[/bold {style}] - {time}",
                            border_style=style,
                            title_align="left",
                            expand=True,
                        )
                    )

                # Update the Live display with the grouped panels
                if display_elements:
                    live.update(Group(*display_elements))

        return ModelResponse(thoughts=thinking_str, content=content_str)

    def reconstruct_history(self, chat_items: list[ChatItem], style: str):
        self.print_system_message(
            "Reconstructing History...", style=style, line_break=True
        )
        if chat_items:
            for item in chat_items:
                if item.role == "user":
                    self.print_user_message(item.message, style=style)
                else:
                    time_of_message = item.created[:19]
                    self.print_assistant_message(
                        item.message,
                        f"Past AI[{style}] - {time_of_message}[/{style}]",
                        style=style,
                    )
