import asyncio
import os
import pathlib

from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich.panel import Panel
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
import shutil

from student_assistant.rag.document_loader import load_and_chunk_docs, load_and_chunk_website
from student_assistant.core.logging import get_logger
from student_assistant.rag.graph.rag_graph import graph
from student_assistant.db import ProjectDB
from student_assistant.CLI import (
    choose_project,
    choose_project_option,
    load_documents,
    confirm_project_deletion,
    new_question,
    ask_document_to_remove,
    confirm_document_removal,
    render_chat_history,
    render_user_message_panel,
    render_assistant_message_panel
)
from student_assistant.project import Project
from student_assistant.rag.vector_store import VectorStore
from student_assistant.rag.memory import history_manager
from student_assistant.core.config import settings


logger = get_logger(__name__)

console = Console()


def main():
    db = ProjectDB()
    while True:
        project = select_project_loop(db)
        project_session(db, project)


def select_project_loop(db: ProjectDB) -> Project:
    project_names = db.list_projects()
    project_name, is_new = choose_project(project_names)
    if is_new:
        db.create_project(project_name)
    return db.get_project_by_name(project_name)


def project_session(db: ProjectDB, project: Project):
    while True:
        option = choose_project_option()

        if option == "❌ Wyjdź":
            raise SystemExit()

        elif option == "🔄 Zmień projekt":
            return 

        elif option == "📄 Wczytaj dokumenty":
            handle_load_documents(project, db)

        elif option == "📖 Przeglądaj dokumenty":
            handle_manage_documents(project, db)
            
        elif option == "🗑️  Usuń projekt":
            if handle_delete_project(project, db):
                return

        elif option == "❓ Zadaj pytanie":
            ask_questions_loop(project.vector_store, project.name)
        
        elif option == "🧹 Wyczyść historię czatu":
            history_manager.clear(project.name)
            console.print("[green]✅ Historia czatu została wyczyszczona.[/green]")


def handle_load_documents(project, db):
    result = load_documents()[0]
    if result == "❌ Anuluj":
        console.print("[green]Anulowano wczytywanie dokumentów.[/green]")
        return

    elif result == "🌐 Wczytaj z URL":
        url = console.input("🔗 Podaj URL do załadowania: ").strip()
        if not url:
            console.print("[red]❗ Nie podano URL.[/red]")
            return

        spinner = Spinner("dots", text=f"Wczytywanie strony {url}...")
        with Live(spinner, refresh_per_second=10):
            file_splits = asyncio.run(load_and_chunk_website(url))

        project.add_documents(file_splits)
        console.print(f"[green]✅ Załadowano stronę i podzielono na {len(file_splits)} chunków.[/green]")

    else:
        if not any(Path(settings.DATA_DIR_PATH).iterdir()) or not any(Path(settings.DATA_DIR_PATH).glob("*.pdf")):
            console.print("❗ [red]Brak dokumentów z rozszerzeniem .pdf do wczytania w katalogu data.[/red]")
            return

        spinner = Spinner("dots", text=f"Wczytywanie dokumentów do projektu: {project.name}...")

        with Live(spinner, refresh_per_second=10):
            file_splits, loaded_file_names = asyncio.run(load_and_chunk_docs(project.name))

        for file_name in loaded_file_names:
            db.add_document(project.id, file_name)

        project.add_documents(file_splits)
        console.print(f"[green]✅ Liczba wczytanych dokumentów: {len(loaded_file_names)}[/green]")


def handle_manage_documents(project, db):
    while True:
        documents = db.list_documents(project.id)

        if not documents:
            console.print("Brak wczytanych dokumentów.")
            return

        selected = ask_document_to_remove(documents)

        if selected == "↩️  Powrót":
            return

        if confirm_document_removal(selected):
            db.delete_document(project.id, selected)
            console.print(f"✅ Dokument '{selected}' został usunięty.")
        else:
            console.print("❎ Anulowano usunięcie.")


def handle_delete_project(project, db) -> bool:
    confirm = confirm_project_deletion(project.name)
    if confirm:
        db.delete_project(project.id)
        shutil.rmtree("loaded_docs/" + project.name, ignore_errors=True)
        console.print(f"Projekt '{project.name}' został usunięty.")
        return True
    else:
        console.print("Nie usunięto projektu.")
        return False
    


def ask_questions_loop(vector_store: VectorStore, project_name: str):
    config = {"configurable": {"thread_id": project_name, "vector_store": vector_store}}
        
    message_history = history_manager.get_message_history(config)
    render_chat_history(console, message_history)

    while True:
        question = new_question()
        
        if not question.strip():
            break

        render_user_message_panel(question, console)
        state = {"messages": [HumanMessage(content=question)]}

        with Live(Spinner("dots", text="Generowanie odpowiedzi..."), refresh_per_second=10):
            result = graph.invoke(state, config=config)
        
        answer = result["messages"][-1].content

        if answer:
            render_assistant_message_panel(answer, console)
        

if __name__ == "__main__":
    main()