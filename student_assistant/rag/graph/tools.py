from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document

from student_assistant.core.logging import get_logger


logger = get_logger(__name__)


def retreive(query: str, config: RunnableConfig) -> list[Document]:
    """
    Retrieve relevant documents from the vector store based on the query.
    """
    vector_store = config["configurable"]["vector_store"]
    retrieved_docs = vector_store.similarity_search(query)
    logger.info(f"Retrieved {len(retrieved_docs)} documents for query: {query}")
    return retrieved_docs