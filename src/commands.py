from view import View
from memory import Memory


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


def handle_command(input_str: str, view: View, memory: Memory) -> None:
    command, args = parse_command(input_str)

    match command:
        case "help":
            handle_help(args, view)

        case "hist":
            handle_hist(args, view, memory)

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


def handle_hist(args, view: View, memory: Memory) -> None:
    if args:
        match args[0]:
            case "list":
                if len(args) < 1:
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
                    chat_data = memory.get_chat_data(int(args[1]))

                    # Reconstruct chat
                    for chat_item in chat_data:
                        id, created, role, message, visible = chat_item
                        if visible > 0:
                            match role:
                                case "user":
                                    view.print_user_message(message)

                                case "assistant":
                                    view.print_assistant_message(message)

            case _:
                view.print_system_message("Unknown request. Available commands:")

    else:
        print("No args given to hist")
