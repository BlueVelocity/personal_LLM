from view import View
from memory import Memory
from engine import AIEngine
from models import ChatItem, ChatHeader
from exceptions import ChatNotFoundError


def parse_command(input_str: str) -> tuple[str, list[str]]:
    """
    Parses command and arguments

    Args:
        input_str: Input command string

    Returns:
        Tuple containing the command and a list of its arguments (command: str, args: [str, ...])
    """
    parts = input_str[1:].strip().split()

    return (parts[0], parts[1:])


def handle_command(
    input_str: str, view: View, memory: Memory, engine: AIEngine, style: str
) -> None:
    """
    Handles command request

    Args:
        input_str: Input command string
        view: Active view object
        memory: Active memory object
        engine: Active engine object
        style: Color of text
    """
    command, args = parse_command(input_str)

    match command:
        case "help":
            handle_help(view, style)

        case "info":
            handle_info(view, memory, engine, style)

        case "list":
            handle_list(args, view, memory, style)

        case "load":
            handle_load(args, view, memory, style)

        case "delete":
            handle_delete(args, view, memory, style)

        case "new":
            handle_new(view, memory, style)

        case _:
            handle_invalid_entry(view, style=style, entry=command)


def handle_help(view: View, style: str) -> None:
    """
    Lists available commands

    Args:
        view: Active view object
        style: Color of text
    """
    view.print_system_message("Controls:", style=style, line_break=True)

    view.print_unordered_list(
        ["ENTER  #Submit", "ALT + ENTER  #New line", "ESC then ENTER  #New line"],
        style=style,
    )

    view.print_system_message("Available commands:", style=style, line_break=True)
    view.print_unordered_list(
        [
            "/info  #Show info about this session",
            "/list \\[qty | None]  #List chat history",
            "/load \\[chat_number]  #Load chat by id",
            "/delete \\[chat_number | '*']  #Delete chat by id",
            "/exit  #Exit the program",
        ],
        style=style,
    )


def handle_info(view: View, memory: Memory, engine: AIEngine, style: str):
    """
    Lists current configuration info

    Args:
        view: Active view object
        memory: Active memory object
        engine: Active engine object
        style: Color of text
    """
    view.print_unordered_list(
        [
            f"Main Model: {engine.model}",
            f"Search Model: {engine.search_model}",
            f"Current Chat ID: {memory.current_id}",
        ],
        style=style,
    )


def handle_list(args, view: View, memory: Memory, style: str) -> None:
    """
    Handles list command requests

    Args:
        args: Arguments passed to list: [qty]
        view: Active view object
        memory: Active memory object
        style: Color of text
    """

    def list_hist(qty: int = 0):
        chat_list: list[ChatHeader] = memory.get_chat_list()

        if qty:
            requested_list: list[ChatHeader] = chat_list[: int(qty)]
        else:
            requested_list: list[ChatHeader] = chat_list

        view.print_table(
            "Chat History",
            ["ID", "Created", "Last Updated", "Title"],
            requested_list,
            col_alignment=["center", "center", "center", "left"],
            expand=True,
            style=style,
        )

        view.print_system_message(
            f"Retrieved {len(requested_list)} of {len(chat_list)} records", style=style
        )

    if args:
        try:
            if len(args) < 1:
                list_hist()
            else:
                list_hist(args[0])
        except ValueError:
            handle_invalid_entry(view, style=style, entry=args[0])
    else:
        list_hist()


def handle_load(args, view: View, memory: Memory, style: str) -> None:
    """
    Handles load command requests

    Args:
        args: Arguments passed to load: [id]
        view: Active view object
        memory: Active memory object
        style: Color of text
    """

    if args:
        try:
            if len(args) < 1:
                handle_invalid_entry(view, style=style, entry=" ")
            else:
                try:
                    memory.set_current_id(int(args[0]))
                    view.reconstruct_history(
                        memory.get_visible_chat_history(), style=style
                    )
                except (ValueError, ChatNotFoundError) as e:
                    view.print_system_message(str(e), style=style, line_break=True)

        except ValueError:
            handle_invalid_entry(view, style=style, entry=args[0])
    else:
        handle_invalid_entry(view, style=style, entry=args[0])


def handle_delete(args, view: View, memory: Memory, style: str) -> None:
    """
    Handles delete command requests

    Args:
        args: Arguments passed to delete: [id]
        view: Active view object
        memory: Active memory object
        style: Color of text
    """

    if args:
        try:
            args[0] = str(args[0])
        except IndexError:
            handle_invalid_entry(view, style=style, entry=args[0])
        else:
            ids_deleted = memory.delete(args[0])
            view.print_system_message(
                f"Deleted {len(ids_deleted)} chats: {', '.join(map(str, ids_deleted))}",
                style=style,
                line_break=True,
            )
    else:
        handle_invalid_entry(view, style=style, entry=args[0])


def handle_new(view: View, memory: Memory, style: str):
    """
    Start new chat

    Args:
        view: Active view object
        style: Color of text
    """
    view.print_system_message("Starting new chat...", line_break=True, style=style)
    memory.current_id = None


def handle_invalid_entry(
    view: View, style: str, entry: str | int, additional_info: str = ""
) -> None:
    view.print_system_message(
        f"Invalid entry: '{entry}'. {additional_info}", style=style
    )
    handle_help(view, style=style)
