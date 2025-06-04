from dataclasses import dataclass

from student_assistant.rag.vector_store import VectorStore


@dataclass
class Project:
    id: int
    name: str
    vector_store: VectorStore = None
    loaded_docs: list[str] = None

    def __post_init__(self):
        self.vector_store = VectorStore(self.name)
    
    def add_documents(self, documents):
        self.vector_store.add_documents(documents)