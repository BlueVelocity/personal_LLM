from view import View
from memory import Memory
from engine import AIEngine
from models import ChatItem


def parse_command(input_str: str) -> tuple[str, list[str]]:
    """
    Parses command and arguments

    Args:
        input_str: Inpurt string

    Returns:
        Tuple containing the command and a list of its arguments (command: str, args: [str, ...])
    """
    parts = input_str[1:].strip().split()

    return (parts[0], parts[1:])


def handle_command(
    input_str: str, view: View, memory: Memory, engine: AIEngine
) -> None:
    command, args = parse_command(input_str)

    match command:
        case "help":
            handle_help(args, view)

        case "hist":
            handle_hist(args, view, memory, engine)

        case _:
            view.print_system_message("Unknown command")


def handle_help(args, view: View) -> None:
    if args:
        match args[0]:
            case "hist":
                view.print_system_message("Available commands:")
                view.print("list \\[qty]\nload \\[chat_number]")

    else:
        view.print_system_message(
            "List of commands:\nhist list \\[qty]\nhist load \\[chat_number]"
        )


def handle_hist(args, view: View, memory: Memory, engine: AIEngine) -> None:
    if args:
        match args[0]:
            case "list":
                if len(args) < 2:
                    args.append(5)
                view.print_ordered_list(
                    [
                        f"{m['date']}: {m['title']}"
                        for m in memory.get_chat_headers(args[1])
                    ],
                    descending=True,
                )

            case "load":
                if len(args) < 1:
                    view.print_system_message(
                        "Please specify chat to load: /hist load \\[chat_number]"
                    )
                else:
                    chat_data: list[tuple[str, str, str, str, int]] = memory.load_chat(
                        int(args[1])
                    )

                    messages = []

                    # Reconstruct chat
                    for chat_item in chat_data:
                        data = ChatItem(*chat_item)

                        messages.append({"role": data.role, "content": data.message})

                        if data.visible > 0:
                            match data.role:
                                case "user":
                                    view.print_user_message(data.message)

                                case "assistant":
                                    view.print_assistant_message(
                                        data.message, engine.model
                                    )

                    engine.messages = messages

            case _:
                view.print_system_message("Unknown request. Available commands:")

    else:
        print("No args given to hist")
