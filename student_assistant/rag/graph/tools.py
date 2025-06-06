from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

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


def web_search(query: str) -> list[Document]:
    """
    Perform a web search and return the results as documents.
    """
    loader = WebBaseLoader(query)
    try:
        docs = loader.load()
        logger.info(f"Web search returned {len(docs)} documents for query: {query}")
        return docs
    except Exception as e:
        logger.error(f"Web search failed for query: {query} with error: {e}")
        return []