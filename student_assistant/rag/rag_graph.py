from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START

from student_assistant.rag.vector_store import VectorStore
from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger
from student_assistant.prompts import prompt


logger = get_logger(__name__)

llm = ChatOpenAI(model=settings.MODEL_NAME)


class State(TypedDict):
    question: str
    context: list[Document]
    answer: str
    vector_store: VectorStore


def retrieve(state: State):
    vector_store = state.get("vector_store")
    retrieved_docs = vector_store.similarity_search(state["question"])
    logger.info(f"Retreived {len(retrieved_docs)} documents for question: {state['question']}")
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()