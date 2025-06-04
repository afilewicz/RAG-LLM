import asyncio

from rich.console import Console
from rich.markdown import Markdown

from student_assistant.document_loader import load_and_chunk_docs
from student_assistant.vector_store import vector_store
from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger
from student_assistant.rag_graph import graph


logger = get_logger(__name__)

console = Console()

async def main():
    file_splits = await load_and_chunk_docs()
    logger.info(f"Loaded {len(file_splits)} {"file" if len(file_splits) == 1 else "files"}.")
    ids = vector_store.add_documents(documents=file_splits)
    logger.info(f"All documents added to vector store at {settings.CHROMA_PATH}.")

    while True:
        question = input("Zadaj pytanie: ")
        if question.lower() == "q":
            break

        state = {"question": question, "context": [], "answer": ""}
        result = graph.invoke(state)
        answer = result["answer"]

        if answer:
            console.print(Markdown("**Odpowiedź asystenta:**"))
            console.print(Markdown(answer))
            console.print("\n---\n")
        

asyncio.run(main())