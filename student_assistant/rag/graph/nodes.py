from pydantic import BaseModel, Field
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, AIMessage

from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger
from student_assistant.prompts import SYSTEM_PROMPT, GRADE_PROMPT, REWRITE_PROMPT
from student_assistant.rag.graph.tools import retreive, web_search


logger = get_logger(__name__)

llm = ChatOpenAI(model=settings.MODEL_NAME)


class State(MessagesState):
    ...


def generate_query_or_respond(state: State):
    """
    Generate a response based on the question and context.
    If no context is provided, generate a query instead.
    """
    logger.info(f"generate_querry_or_respond called with messages: {state["messages"]}")
    response = llm.bind_tools([retreive, web_search]).invoke(state['messages'])
    return {"messages": response}


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'tak' if relevant, or 'nie' if not relevant"
    )


def grade_documents(state: State) -> Literal["generate_answer", "rewrite_question"]:
    logger.info(f"grade_documents called with messages: {state["messages"]}")

    messages = state["messages"]

    question = next(
        msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)
    )
    recent_messages = messages[-5:] if len(messages) > 5 else messages
    context_parts = [
        msg.content for msg in recent_messages
        if isinstance(msg, (HumanMessage, AIMessage))
    ]
    context = "\n".join(context_parts)

    prompt = GRADE_PROMPT.invoke({"question": question, "context": context})
    response = llm.with_structured_output(GradeDocuments).invoke(prompt)

    score = response.binary_score

    return "generate_answer" if score == "tak" else "rewrite_question"


# def rewrite_question(state: State) -> State:
#     logger.info(f"rewrite_question called with messages: {state["messages"]}")
#     messages = state["messages"]
#     question = messages[0].content
#
#     prompt = REWRITE_PROMPT.invoke({"question": question})
#     response = llm.invoke(prompt)
#
#     return {"messages": [{"role": "user", "content": response.content}]}
def rewrite_question(state: State) -> State:
    logger.info(f"rewrite_question called with messages: {state['messages']}")
    messages = state["messages"]

    original_question = next(
        msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)
    )

    prompt = REWRITE_PROMPT.invoke({"question": original_question})
    response = llm.invoke(prompt)

    new_messages = []
    found_last_human = False
    for msg in messages[::-1]:
        if isinstance(msg, HumanMessage) and not found_last_human:
            found_last_human = True
            continue
        new_messages.append(msg)
    new_messages = new_messages[::-1]

    new_messages.append(HumanMessage(content=response.content))

    return {"messages": new_messages}



def generate_answer(state: State) -> State:
    logger.info(f"generate_answer called with messages: {state["messages"]}")
    messages = state["messages"]

    question = next(
        msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage)
    )

    recent_messages = messages[-5:] if len(messages) > 5 else messages
    context_parts = [
        msg.content for msg in recent_messages
        if isinstance(msg, (HumanMessage, AIMessage))
    ]
    context = "\n".join(context_parts)

    prompt = SYSTEM_PROMPT.invoke({"question": question, "context": context})
    response = llm.invoke(prompt)

    return {"messages": [response]}