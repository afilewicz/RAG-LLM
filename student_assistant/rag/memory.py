from dataclasses import dataclass, field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


@dataclass
class ChatHistoryManager:
    db_path: str = "sqlite/graph_checkpoints.db"
    checkpointer: SqliteSaver = field(init=False)

    def __post_init__(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(conn)

    def get_message_history(self, config: RunnableConfig):
        checkpoint = self.checkpointer.get(config)
        if checkpoint is None:
            return []
        channel_values = checkpoint["channel_values"]
        if channel_values is None:
            return []

        messages = channel_values.get("messages", [])

        return [
            msg for msg in messages if isinstance(msg, (HumanMessage, AIMessage))
        ]

    def clear(self, thread_id: str):
        self.checkpointer.delete_thread(thread_id)


history_manager = ChatHistoryManager()