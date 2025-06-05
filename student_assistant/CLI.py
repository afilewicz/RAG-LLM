from InquirerPy import inquirer
from InquirerPy.separator import Separator
from student_assistant.core.config import settings


def enter_new_project_name(existing_names: list) -> str:
    return inquirer.text(
        message="Podaj nazwę nowego projektu:",
        validate=lambda x: len(x) > 0 and x not in existing_names,
        invalid_message="Projekt o takiej nazwie już istnieje.",
    ).execute()


def choose_project(project_names: list[str]) -> tuple[str, bool]:
    choices = [Separator(), *project_names, Separator(), "➕ Utwórz nowy projekt", "❌ Wyjdź"]
    selected = inquirer.select(
        message="Wybierz projekt lub utwórz nowy:",
        choices=choices,
        default=0
    ).execute()

    if selected == "➕ Utwórz nowy projekt":
        new_name = enter_new_project_name(project_names)
        return new_name, True

    elif selected == "❌ Wyjdź":
        raise SystemExit()

    return selected, False


def choose_project_option() -> str:
    choices = [
        Separator(),
        "📄 Wczytaj dokumenty",
        "📖 Przeglądaj dokumenty",
        "❓ Zadaj pytanie",
        "🔄 Zmień projekt",
        "🗑️  Usuń projekt",
        Separator(),
        "❌ Wyjdź"
    ]

    return inquirer.select(
        message="Co chcesz zrobić:",
        choices=choices,
        default=0
    ).execute()


def load_documents():
    return inquirer.select(
        message=f"Umieść dokumenty w katalogu {settings.DATA_DIR_PATH} i naciśnij Enter, aby kontynuować.",
        choices=["📂 Wczytaj dokumenty", "❌ Anuluj"]
        ).execute(),


def confirm_project_deletion(project_name: str) -> bool:
    return inquirer.confirm(
        message=f"Czy na pewno chcesz usunąć projekt '{project_name}'?",
        default=False
    ).execute()


def new_question() -> str:
    return inquirer.text(
            message="Zadaj pytanie (pozostaw puste i naciśnij Enter, aby zakończyć):"
        ).execute()


def ask_document_to_remove(documents: list[str]) -> str:
    choices = [Separator(), *documents, Separator(),"↩️  Powrót"]
    return inquirer.select(
        message="Jeżeli chcesz usunąć dokument, zaznacz go i kliknij Enter:",
        choices=choices,
        default=0,
    ).execute()


def confirm_document_removal(document_name: str) -> bool:
    return inquirer.confirm(
        message=f"Czy na pewno chcesz usunąć dokument '{document_name}'?",
        default=True
    ).execute()