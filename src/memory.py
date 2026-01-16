import os
from pathlib import Path
import sqlite3
from datetime import datetime
import random
import string
from models import ChatHeader


class Memory:
    """Provides connection to the chat history database"""

    def __init__(self):
        self.current_chat_id: str = ""
        self.db_path: Path = Path(__file__).resolve().parent.parent / "memory.db"
        self._initialize_db()

    def _generate_id(self, dt: datetime):
        dt_str = dt.strftime("%Y%m%dT%H%M%S%f")
        random_str = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        return f"{dt_str}{random_str}"

    def _initialize_db(self):
        """Checks if database exists and initializes the database by creating tables if it does not"""
        if os.path.exists(self.db_path):
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()
        else:
            self.db = sqlite3.connect(self.db_path)
            self.cursor = self.db.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")

            # table with ID, TITLE, and CREATED
            self.cursor.execute("""
                CREATE TABLE chats(
                    id TEXT PRIMARY KEY, 
                    created TEXT,
                    title TEXT 
                )
            """)

            # table with CHAT_ID, role (system, user, or assistant), and content
            self.cursor.execute("""
                CREATE TABLE chat_history(
                    chat_id TEXT, 
                    created TEXT,
                    role TEXT,
                    content TEXT,
                    visible INTEGER,
                    FOREIGN KEY (chat_id) REFERENCES chats(id)
                )
            """)

            self.db.commit()

    def _convert_to_chat_data_format(self, data: tuple) -> list[dict[str, str] | int]:
        """
        Converts tuple provided from chat_history into a formatted dictionary

        Args:
            data: Tuple containing (chat_id, created, role, content, visible)

        Returns:
            Dictionary with {role: str, content: str, visible: int} fields
        """
        return [{"role": data[2], "content": data[3]}, data[4]]

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
        datetime_created = datetime.now()
        id = self._generate_id(datetime_created)

        self.cursor.execute(
            "INSERT INTO chats VALUES(?,?,?)", (id, datetime_created, title)
        )
        self.db.commit()

    def add_to_conversation(self, role: str, content: str, visible: int) -> None:
        """
        Adds a content to conversation history

        Args:
            role: Who the content is from (system, assistant, or user)
            content: content to store
            visible: Whether the content is visible to the user or not (0 no, >0 yes)

        Example:
            add_to_conversation("20260111T11471938829023l5ohLg", "user", "What is the weather tomorrow?", 0)
        """
        datetime_created = datetime.now()

        self.cursor.execute(
            "INSERT INTO chat_history VALUES (?,?,?,?,?)",
            (self.current_chat_id, datetime_created, role, content, visible),
        )

        self.db.commit()

    def get_chat_headers(self, limit: str | int = 0) -> list[ChatHeader]:
        """
        Retrieves the chat titles from memory

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

    def load_chat(self, pos: int) -> list[tuple[str, str, str, str, int]]:
        chat_id = self.cursor.execute(
            "SELECT * FROM chats ORDER BY created DESC"
        ).fetchall()[pos][0]

        self.current_chat_id = chat_id

        chat_data = self.cursor.execute(
            f"SELECT * FROM chat_history WHERE chat_id='{chat_id}' ORDER BY created ASC"
        ).fetchall()

        return chat_data
