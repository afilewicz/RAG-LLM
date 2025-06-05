from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from student_assistant.rag.graph.nodes import (
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
    generate_answer,
    State
)
from student_assistant.rag.graph.tools import retreive


workflow = StateGraph(State)

workflow.add_node(generate_query_or_respond)
workflow.add_node("retrieve", ToolNode([retreive]))
workflow.add_node(rewrite_question)
workflow.add_node(generate_answer)

workflow.add_edge(START, "generate_query_or_respond")

workflow.add_conditional_edges(
    "generate_query_or_respond",
    tools_condition,
    {
        "tools": "retrieve",
        END: END,
    },
)

workflow.add_conditional_edges(
    "retrieve",
    grade_documents,
)
workflow.add_edge("generate_answer", END)
workflow.add_edge("rewrite_question", "generate_query_or_respond")

conn = sqlite3.connect("sqlite/graph_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = workflow.compile(checkpointer=checkpointer)

with open("graph_visualization.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())