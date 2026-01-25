import os
from pathlib import Path
import sqlite3
from datetime import datetime
from models import ChatHeader, ChatItem
from exceptions import ChatNotFoundError
from datetime import date


class Memory:
    """Provides connection to the chat history database"""

    def __init__(self):
        self.current_id: int | None = None
        self.db_path: Path = Path(__file__).resolve().parent.parent / "memory.db"
        self._initialize_db()

    def _initialize_db(self):
        """Checks if database exists and initializes the database by creating tables if it does not"""
        if os.path.exists(self.db_path):
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()
        else:
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")

            self.cursor.execute("""
                CREATE TABLE chats(
                    id INTEGER PRIMARY KEY, 
                    created TEXT,
                    title TEXT 
                )
            """)

            self.cursor.execute("""
                CREATE TABLE chat_history(
                    id INTEGER, 
                    created TEXT,
                    role TEXT,
                    content TEXT,
                    visible INTEGER,
                    FOREIGN KEY (id) REFERENCES chats(id)
                )
            """)

            self.db.commit()

    @staticmethod
    def _update_chat_date(func):
        """
        Updates the created field of the current chat to the current datetime
        """

        def wrapper(self, *args):
            func(self, *args)

            updated_datetime = datetime.now()
            self.cursor.execute(
                "UPDATE chats SET created = ? WHERE id=?",
                (updated_datetime, self.current_id),
            )
            self.db.commit()

        return wrapper

    def create_conversation(self, title: str) -> None:
        """
        Creates a new conversation in the database

        Args:
            title: Title of chat instance

        Returns:
            Chat instance id

        Example:
            create_conversation("What is the weather tomorrow?")
        """
        created = datetime.now()

        self.cursor.execute(
            "INSERT INTO chats (created, title) VALUES (?,?)", (created, title)
        )
        generated_id = self.cursor.lastrowid

        self.db.commit()

        self.current_id = generated_id

    @_update_chat_date
    def _add_to_conversation(self, role: str, content: str, visible: int) -> None:
        """
        Adds a content to conversation history

        Args:
            role: Who the content is from (system, assistant, or user)
            content: content to store
            visible: Whether the content is visible to the user or not
                0 is False, >0 is True

        Example:
            add_to_conversation("20260111T11471938829023l5ohLg", "user", "What is the weather tomorrow?", 0)
        """
        created = datetime.now()

        self.cursor.execute(
            "INSERT INTO chat_history VALUES (?,?,?,?,?)",
            (self.current_id, created, role, content, visible),
        )

        self.db.commit()

    def add_user_message(self, content: str):
        """
        Adds a user message to the message log

        Args:
            content: Content to add to user message
        """
        self._add_to_conversation("user", content, 1)

    def add_assistant_message(self, content: str):
        """
        Adds a assistant message to the message log

        Args:
            content: Content to add to assistant message
        """
        self._add_to_conversation("assistant", content, 1)

    def add_system_message(
        self, initial_context: str, initial_instructions: str, user_data: str
    ) -> None:
        """
        Adds a system message to the message log

        Args:
            content: Content to add to assistant message
        """
        content = f"CONTEXT: {initial_context}\nCURRENT DATE: {date.today()}\nINSTRUCTIONS: {initial_instructions}\nUSER DATA: {user_data}"
        self._add_to_conversation("system", content, 0)

    def add_search_message(self, content: str):
        """
        Adds a search message to the message log

        Args:
            content: Content to add to the search message
        """
        content = f"INTERNET SEARCH RESULTS:\n{content}"
        self._add_to_conversation("user", content, 0)

    def delete(self, id: str | int) -> list[int]:
        """
        Deletes a specific chat or all chats (excluding the current one) from history.

        Args:
            id: The unique identifier of the chat to delete.
                Pass "*" to delete all chats except the current session.

        Returns:
            list[int]: List of chat IDs successfully deleted from the database.

        Note:
            The current session (self.current_id) cannot be deleted using this method.
            If the current ID is passed, the function returns an empty list.

        Example:
            memory.delete(4)
            memory.delete("*")  # Clear all except active
        """
        id_str = str(id)

        if id_str == str(self.current_id):
            return []

        if id_str == "*":
            if self.current_id:
                query = "DELETE FROM chats WHERE id != ?"
                params = (self.current_id,)
            else:
                query = "DELETE FROM chats"
                params = ()
        else:
            query = "DELETE FROM chats WHERE id = ?"
            params = (id_str,)

        select_query = query.replace("DELETE", "SELECT id")
        ids_deleted = [
            row[0] for row in self.cursor.execute(select_query, params).fetchall()
        ]

        self.cursor.execute(query, params)
        history_query = query.replace("FROM chats", "FROM chat_history")
        self.cursor.execute(history_query, params)

        self.db.commit()

        return ids_deleted

    def get_chat_list(self, limit: str | int = 0) -> list[ChatHeader]:
        """
        Retrieves the chat ids and titles from memory

        Args:
            limit: Limit of results. Leave empty for all records

        Returns:
            List of dictionaries containing [{"date": str, "title": str}, ...]
        """
        if type(limit) is str:
            limit = int(limit)

        if limit:
            chat_headers = reversed(
                self.cursor.execute(
                    f"SELECT * FROM chats ORDER BY created DESC LIMIT {limit}"
                ).fetchall()
            )
        else:
            chat_headers = self.cursor.execute(
                "SELECT * FROM chats ORDER BY created ASC"
            ).fetchall()

        chat_list = []
        for chat_header in chat_headers:
            chat_list.append(ChatHeader(*chat_header))

        return chat_list

    def _get_all_chat_ids(self) -> list[int]:
        ids = [row[0] for row in self.cursor.execute("SELECT * FROM chats").fetchall()]

        return ids

    def set_current_id(self, id: int) -> None:
        if id == self.current_id:
            raise ChatNotFoundError("ID currently loaded")

        if id not in self._get_all_chat_ids():
            raise ChatNotFoundError("ID does not exist")

        self.current_id = id

    def _get_chat_records(self, id: int) -> list[ChatItem]:
        """
        Retrieves a list of records by chat id from the database

        Args:
            id: id number of the chat

        Returns:
            List of tuples containing individual message data
        """
        chat_records = self.cursor.execute(
            f"SELECT * FROM chat_history WHERE id='{id}' ORDER BY created ASC"
        ).fetchall()

        output = [ChatItem(*row) for row in chat_records]

        return output

    def get_llm_formatted_chat_history(self) -> list[dict[str, str]]:
        """
        Retrieves chat logs in llm format

        Returns:
            List of dictionaries with {role, content} ollama format
        """

        def format_history(item: ChatItem) -> dict[str, str]:
            return {"role": item.role, "content": item.message}

        if self.current_id is None:
            return []
        else:
            formatted_chat_history = list(
                map(format_history, self._get_chat_records(self.current_id))
            )

        return formatted_chat_history

    def get_visible_chat_history(
        self,
    ) -> list[ChatItem]:
        """
        Retrieves chat logs in chat reconstruction format for display

        Returns:
            List of dictionaries with [{roles, content}, visible]
        """

        chat_history = []

        if self.current_id is None:
            return []
        else:
            for item in self._get_chat_records(self.current_id):
                if int(item.visible):
                    chat_history.append(item)

        return chat_history
