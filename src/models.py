from typing import NamedTuple


class ModelResponse(NamedTuple):
    thoughts: str
    content: str


class ChatItem(NamedTuple):
    id: str
    created: str
    role: str
    message: str
    visible: int


class ChatHeader(NamedTuple):
    id: str
    created: str
    updated: str
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
    assistant_text: str
    user: str
    header: str
    warning: str
    text: str


class UserData(NamedTuple):
    user_data: str
