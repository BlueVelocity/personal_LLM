from typing import NamedTuple


class ChatItem(NamedTuple):
    id: str
    created: str
    role: str
    message: str
    visible: int


class ChatHeader(NamedTuple):
    id: str
    created: str
    title: str


class ModelConfig(NamedTuple):
    main_model: str
    search_model: str
    keep_alive: int
    main_thinking: bool
    search_thinking: bool
    initial_context: str
    system_instructions: str


class SearchConfig(NamedTuple):
    search_engine: str
    search_headers: str


class StyleConfig(NamedTuple):
    system: str
    assistant: str
    user: str

    # main_model: str = config["models"]["MAIN"]
    # search_term_model: str = config["models"]["SEARCH"]
    #
    # keep_alive: int = config["model_settings"]["keep_alive"]
    # main_thinking: bool = config["model_settings"]["allow_main_thinking"]
    # search_thinking: bool = config["model_settings"]["allow_search_thinking"]
    #
    # initial_context: str = config["system_prompt"]["initial_context"]
    # initial_instructions: str = config["system_prompt"]["system_instructions"]
    #
    # search_engine: str = config["search_settings"]["engine_name"]
    # search_headers: str = config["search_settings"]["headers"]
