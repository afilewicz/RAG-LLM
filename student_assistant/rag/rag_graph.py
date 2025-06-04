from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, MessagesState, END
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition

from student_assistant.rag.vector_store import VectorStore
from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger
from student_assistant.prompts import prompt


logger = get_logger(__name__)

llm = ChatOpenAI(model=settings.MODEL_NAME)


class State(MessagesState):
    question: str
    context: list[Document]
    answer: str
    vector_store: VectorStore

@tool(response_format="content_and_artifact")
def retrieve(query: str, vector_store: VectorStore):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs
    logger.info(f"Retreived {len(retrieved_docs)} documents for question: {state['question']}")
    return {"context": retrieved_docs}


def query_or_respond(state: MessagesState):
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

tools = ToolNode([retrieve])

def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()

# png_data = graph.get_graph().draw_mermaid_png()
#
# with open("graph_output.png", "wb") as f:
#     f.write(png_data)