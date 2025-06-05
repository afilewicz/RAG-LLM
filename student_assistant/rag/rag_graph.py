from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from openai import vector_stores
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, MessagesState, END
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition

from student_assistant.rag.vector_store import VectorStore
from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger
from typing import Callable

from student_assistant.prompts import prompt


logger = get_logger(__name__)

llm = ChatOpenAI(model=settings.MODEL_NAME)


class State(MessagesState):
    question: str
    context: list[Document]
    answer: str
    vector_store: VectorStore

def perform_retrieval(query: str, vector_store_instance: VectorStore) -> tuple[str, list[Document]]:
    logger.info(f"Performing retrieval for query: '{query}' using vector_store: {vector_store_instance.project_name}")
    retrieved_docs = vector_store_instance.similarity_search(query, k=2)
    if not retrieved_docs:
        logger.warning("No documents found by similarity search.")
        return "W dostarczonych dokumentach nie znaleziono pasujących informacji.", []

    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

@tool
def retrieve_documents_for_llm(query: str):
    """
    Retrieve documents relevant to the user's query.
    Use this tool to fetch information before answering a question.
    """
    # Ta funkcja jest bardziej specyfikacją dla LLM.
    # Można tu zwrócić placeholder lub nawet query, jeśli jest to potrzebne do debugowania.
    # Ważne jest, aby nazwa tej funkcji była używana do identyfikacji wywołania narzędzia.
    return f"Placeholder for retrieving documents for query: {query}"


def custom_tool_executor_node(state: State) -> dict:
    tool_messages_to_add = []
    last_message = state["messages"][-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        logger.info("No tool calls in the last message.")
        return {"messages": []}

    vector_store_instance = state.get("vector_store")
    if not vector_store_instance:
        logger.error("VectorStore not found in state for custom_tool_executor_node!")
        # Można dodać ToolMessage z błędem
        # Na razie zwracamy puste, co spowoduje odpowiedź "brak informacji"
        return {"messages": []}


    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get("name") # W nowszych wersjach może być tool_call.name
        if not tool_name: # Sprawdzenie dla starszych wersji, gdzie tool_call to słownik
             tool_name = tool_call.get("name")


        logger.info(f"Tool call received: {tool_name}, args: {tool_call.get('args')}")

        # Sprawdź, czy nazwa narzędzia z tool_call pasuje do nazwy narzędzia, które zdefiniowałeś dla LLM
        if tool_name == retrieve_documents_for_llm.name: # Poprawka tutaj
            query = tool_call.get("args", {}).get("query")
            if query:
                try:
                    serialized_content, retrieved_docs_artifacts = perform_retrieval(query, vector_store_instance)
                    tool_messages_to_add.append(ToolMessage(
                        content=serialized_content,
                        tool_call_id=tool_call.get("id"),
                        name=tool_name,
                    ))
                    logger.info(f"Successfully executed tool '{tool_name}' and added ToolMessage.")
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                    tool_messages_to_add.append(ToolMessage(
                        content=f"Błąd podczas wykonywania narzędzia {tool_name}: {e}",
                        tool_call_id=tool_call.get("id"),
                        name=tool_name,
                    ))
            else:
                logger.warning(f"Missing 'query' argument for tool {tool_name}")
                tool_messages_to_add.append(ToolMessage(
                    content=f"Brak argumentu 'query' dla narzędzia {tool_name}",
                    tool_call_id=tool_call.get("id"),
                    name=tool_name,
                ))
        else:
            logger.warning(f"Unknown tool called: {tool_name}")
            tool_messages_to_add.append(ToolMessage(
                content=f"Nieznane narzędzie: {tool_name}",
                tool_call_id=tool_call.get("id"),
                name=tool_name,
            ))

    return {"messages": tool_messages_to_add}

# Węzeł query_or_respond - LLM decyduje
def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    # Ważne: przekazujemy retrieve_documents_for_llm, a nie oryginalne retrieve
    llm_with_tools = llm.bind_tools([retrieve_documents_for_llm])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# Węzeł generate - bez zmian, ale upewnij się, że logowanie jest pomocne
def generate(state: State):
    """Generate answer."""
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Lepsze logowanie
    logger.info(f"Generate node: Found {len(tool_messages)} tool messages.")
    for i, tm in enumerate(tool_messages):
        logger.info(f"Generate node: ToolMessage {i} (ID: {tm.tool_call_id}, Name: {tm.name}) content: '{tm.content[:200]}...'")
        # Jeśli używasz additional_kwargs={"artifact": ...} w ToolMessage:
        # if hasattr(tm, 'additional_kwargs') and 'artifact' in tm.additional_kwargs:
        #    logger.info(f"Generate node: ToolMessage {i} has {len(tm.additional_kwargs['artifact'])} artifacts.")


    docs_content = "\n\n".join(doc.content for doc in tool_messages if doc.content and "Błąd podczas wykonywania narzędzia" not in doc.content) # Filtruj błędy

    system_message_content = (
        "Jesteś pomocnym asystentem studenta."
        "Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów."
        "Jeżeli czegoś nie ma w dokumentach napisz że nie ma tej informacji w dostarczonych dokumentach."
        "\n\n"
        f"{docs_content}" # docs_content może być teraz pusty, jeśli retrieval się nie powiódł lub nic nie znalazł
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not (hasattr(message, "tool_calls") and message.tool_calls) ) # Nie dodawaj AI message, które tylko wywoływało narzędzie
    ]
    # Usuń ostatnią wiadomość AI, jeśli była to wiadomość z tool_calls
    if conversation_messages and hasattr(conversation_messages[-1], "tool_calls") and conversation_messages[-1].tool_calls:
         conversation_messages.pop()


    prompt_messages = [SystemMessage(content=system_message_content)] + conversation_messages

    logger.info(f"Generate node: Prompting LLM with SystemMessage and {len(conversation_messages)} other messages.")
    response = llm.invoke(prompt_messages)
    return {"messages": [response]}


# Budowanie grafu
graph_builder = StateGraph(State)
graph_builder.add_node("query_or_respond", query_or_respond)
graph_builder.add_node("tools", custom_tool_executor_node) # Użyj niestandardowego węzła
graph_builder.add_node("generate", generate)

graph_builder.set_entry_point("query_or_respond")

graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition, # tools_condition sprawdza, czy ostatnia wiadomość ma tool_calls
    {END: END, "tools": "tools"}, # Jeśli są tool_calls, idź do "tools", inaczej do END
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()