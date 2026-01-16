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
