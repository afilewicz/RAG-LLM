from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import VectorStore as LangchainVectorStore
from dataclasses import dataclass, field

from student_assistant.core.config import settings


embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)


@dataclass
class VectorStore:
    project_name: str
    store: LangchainVectorStore = field(init=False)

    def __post_init__(self):
        self.store = Chroma(
            collection_name=self._get_collection_name(),
            persist_directory=settings.CHROMA_PATH,
            embedding_function=embeddings
        )

    def add_documents(self, documents):
        return self.store.add_documents(documents)

    def similarity_search(self, query, k=5):
        return self.store.similarity_search(query, k=k)

    def _get_collection_name(self) -> str:
        return f"student_assistant_{self.project_name}"
