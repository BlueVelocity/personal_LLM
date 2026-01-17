from sqlite3 import OperationalError
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
    input_str: str, view: View, memory: Memory, engine: AIEngine
) -> None:
    """
    Handles command request

    Args:
        input_str: Input command string
        view: Active view object
        memory: Active memory object
        engine: Active engine object
    """
    command, args = parse_command(input_str)

    match command:
        case "help":
            handle_help(view)

        case "hist":
            handle_hist(args, view, memory, engine)

        case _:
            view.print_system_message("Unknown command")
            handle_help(view)


def handle_help(view: View) -> None:
    """
    Lists available commands

    Args:
        view: Active view object
    """
    view.print_system_message("Available commands:")
    view.print_unordered_list(
        ["/hist list \\[qty | None]", "/hist load \\[chat_number]", "/exit"]
    )


def handle_hist(args, view: View, memory: Memory, engine: AIEngine) -> None:
    """
    Handles hist command requests

    Args:
        args: Arguments to be requested from hist
        view: Active view object
        memory: Active memory object
        engine: Active engine object
    """
    if args:
        match args[0]:
            case "list":
                if len(args) < 2:
                    args.append(5)

                chat_list: list[ChatHeader] = memory.get_chat_list(args[1])

                view.print_table(
                    "Chat History",
                    ["ID", "Date-Time Created", "Title"],
                    chat_list,
                    col_alignment=["center", "center", "left"],
                    expand=True,
                    style="cyan",
                )

                view.print_system_message(f"Retrieved {len(chat_list)} records")

            # case "load":
            #     if len(args) < 1:
            #         view.print_system_message(
            #             "Please specify chat to load: /hist load \\[chat_number]"
            #         )
            #     else:
            #         chat_data: list[tuple[str, str, str, str, int]] = memory.load_chat(
            #             int(args[1])
            #         )
            #
            #         messages = []
            #
            #         # Reconstruct chat
            #         for chat_item in chat_data:
            #             data = ChatItem(*chat_item)
            #
            #             messages.append({"role": data.role, "content": data.message})
            #
            #             if data.visible > 0:
            #                 match data.role:
            #                     case "user":
            #                         view.print_user_message(data.message)
            #
            #                     case "assistant":
            #                         view.print_assistant_message(
            #                             data.message, engine.model
            #                         )
            #
            #         engine.messages = messages
            #
            case "delete":
                try:
                    args[1] = str(args[1])
                except IndexError:
                    view.print_system_message(
                        "Please provide an argument to delete: int or '*'"
                    )
                else:
                    qty_chats_deleted = memory.delete(args[1])
                    view.print_system_message(f"Deleted {qty_chats_deleted} chats")

            case _:
                view.print_system_message("Unknown hist request.")
                handle_help(view)

    else:
        print("No args given to hist")
