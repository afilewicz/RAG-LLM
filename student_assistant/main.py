import asyncio

from rich.console import Console
from rich.markdown import Markdown

from student_assistant.rag.document_loader import load_and_chunk_docs
from student_assistant.core.logging import get_logger
from student_assistant.rag.rag_graph import graph
from student_assistant.db import ProjectDB
from student_assistant.CLI import (
    choose_project,
    choose_project_option,
    load_documents,
    confirm_project_deletion,
    new_question
)
from student_assistant.project import Project
from student_assistant.rag.vector_store import VectorStore


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


def handle_load_documents(project, db):
    load_documents()
    console.print(f"Wczytywanie dokumentów do projektu: {project.name}...")
    file_splits, loaded_file_names = asyncio.run(load_and_chunk_docs())
    
    for file_name in loaded_file_names:
        db.add_document(project.id, file_name)
    
    project.add_documents(file_splits)
    console.print(f"Liczba wczytanych dokumentów: {len(loaded_file_names)}")


def handle_view_documents(project, db):
    documents = db.list_documents(project.id)
    if documents:
        console.print("Wczytane dokumenty:")
        for doc in documents:
            console.print(f"- {doc}")
    else:
        console.print("Brak wczytanych dokumentów.")


def handle_delete_project(project, db) -> bool:
    confirm = confirm_project_deletion(project.name)
    if confirm:
        db.delete_project(project.id)
        console.print(f"Projekt '{project.name}' został usunięty.")
        return True
    else:
        console.print("Nie usunięto projektu.")
        return False


def project_session(db: ProjectDB, project: Project):
    while True:
        option = choose_project_option()

        if option == "❌ Wyjdź":
            raise SystemExit()

        elif option == "🔄 Zmień projekt":
            return 

        elif option == "📄 Wczytaj dokumenty":
            handle_load_documents(project, db)

        elif option == "📖 Zobacz wczytane dokumenty":
            handle_view_documents(project, db)
            
        elif option == "🗑️  Usuń projekt":
            handle_delete_project(project, db)
        
        elif option == "❓ Zadaj pytanie":
            ask_questions_loop(project.vector_store)


def ask_questions_loop(vector_store: VectorStore):
    while True:
        question = new_question()

        if not question.strip():
            console.print("[grey]Zakończono sesję pytań.[/grey]")
            break

        state = {"question": question, "context": [], "answer": "", "vector_store": vector_store}
        result = graph.invoke(state)
        answer = result["answer"]

        if answer:
            console.print(Markdown("**Odpowiedź asystenta:**"))
            console.print(Markdown(answer))
            console.print("\n---\n")
        

if __name__ == "__main__":
    main()