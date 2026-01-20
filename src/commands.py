from view import View
from memory import Memory
from engine import AIEngine
from models import ChatItem, ChatHeader


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
            handle_info(view, engine, style)

        case "hist":
            handle_hist(args, view, memory, engine, style)

        case _:
            handle_invalid_entry(view, style=style, entry=command)


def handle_help(view: View, style: str) -> None:
    """
    Lists available commands

    Args:
        view: Active view object
        style: Color of text
    """
    view.print_system_message("Available commands:", style=style, line_break=True)
    view.print_unordered_list(
        [
            "/info #Show info about this session",
            "/hist list \\[qty | None] #List chat history",
            "/hist load \\[chat_number] #Load chat from history",
            "/hist delete \\[chat_number | '*'] #Load chat from history",
            "/exit #Exit the program",
        ],
        style=style,
    )


def handle_info(view: View, engine: AIEngine, style: str):
    """
    Lists current configuration info

    Args:
        view: Active view object
        style: Color of text
    """
    view.print_unordered_list(
        [f"Model: {engine.model}", f"Search Model: {engine.search_model}"], style=style
    )


def handle_hist(args, view: View, memory: Memory, engine: AIEngine, style: str) -> None:
    """
    Handles hist command requests

    Args:
        args: Arguments to be requested from hist
        view: Active view object
        memory: Active memory object
        engine: Active engine object
        style: Color of text
    """

    def list_hist(qty: int = 0):
        chat_list: list[ChatHeader] = memory.get_chat_list(qty)

        view.print_table(
            "Chat History",
            ["ID", "Date-Time Created", "Title"],
            chat_list,
            col_alignment=["center", "center", "left"],
            expand=True,
            style=style,
        )

        view.print_system_message(f"Retrieved {len(chat_list)} records", style=style)

    if args:
        match args[0]:
            case "list":
                try:
                    if len(args) < 2:
                        list_hist()
                    else:
                        list_hist(args[1])
                except ValueError:
                    handle_invalid_entry(view, style=style, entry=args[1])
            case "load":
                try:
                    if len(args) < 2:
                        handle_invalid_entry(view, style=style, entry=" ")
                    else:
                        # Check if current id, if so, print response and do nothing
                        try:
                            memory.set_current_id(int(args[1]))
                            view.reconstruct_history(
                                memory.get_visible_chat_history(), style=style
                            )
                        except Exception as e:
                            view.print_system_message(str(e), style=style)

                except ValueError:
                    handle_invalid_entry(view, style=style, entry=args[1])

            case "delete":
                try:
                    args[1] = str(args[1])
                except IndexError:
                    handle_invalid_entry(view, style=style, entry=args[1])
                else:
                    ids_deleted = memory.delete(args[1])
                    view.print_system_message(
                        f"Deleted {len(ids_deleted)} chats: {', '.join(map(str, ids_deleted))}",
                        style=style,
                    )

            case _:
                handle_invalid_entry(view, style=style, entry=args[0])

    else:
        list_hist()


def handle_invalid_entry(
    view: View, style: str, entry: str | int, additional_info: str = ""
) -> None:
    view.print_system_message(
        f"Invalid entry: '{entry}'. {additional_info}", style=style
    )
    handle_help(view, style=style)
