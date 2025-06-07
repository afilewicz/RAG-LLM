# Asystent nauki do kolokwium – Dokumentacja

## Opis ogólny

Aplikacja CLI wspomagająca studentów w pracy z dokumentami. Pozwala zarządzać projektami, wczytywać dokumenty (lokalne i online), zadawać pytania na podstawie treści dokumentów oraz zarządzać historią czatu. Dane przechowywane są w lokalnej bazie SQLite. Aplikacja używa RAG (Retrieval-Augmented Generation) z LangChainem.

---

##  Struktura głównych komponentów

### CLI – Interfejs użytkownika (tekstowy)

Z wykorzystaniem **InquirerPy** realizowane są:

- Wybór projektu (istniejącego lub nowego),
- Wybór opcji: ładowanie/przeglądanie dokumentów, zadawanie pytań, czyszczenie historii, usuwanie/zamiana projektu,
- Potwierdzenia akcji (usuwanie projektów/dokumentów),
- Interaktywne wprowadzanie pytań.

### Konsola – Wyświetlanie wyników

Z użyciem **rich.console**, **rich.panel** i **rich.markdown**, aplikacja:

- Renderuje wiadomości użytkownika i asystenta w stylizowanych panelach,
- Pokazuje historię czatu,
- Informuje o stanie operacji (np. spinner przy ładowaniu danych).

---

##  Baza danych

Używana baza danych **SQLite** zawiera dwie tabele:

```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### Możliwości

- Tworzenie i usuwanie projektów,
- Dodawanie i usuwanie dokumentów z projektu,
- Pobieranie listy projektów i dokumentów,
- Pobieranie ID projektu po nazwie.

---

## Praca z dokumentami

### Wczytywanie

Obsługiwane źródła:

- 📄 Pliki `.pdf` z katalogu `data/`
- 🌐 Strony internetowe (URL)

Dokumenty są dzielone na fragmenty i przekazywane do **wektorowej bazy wiedzy (VectorStore)**.

### Przeglądanie i usuwanie

Użytkownik może:

- Przeglądać listę dokumentów w projekcie,
- Wybierać i usuwać wybrane pliki.

---

## Zadawanie pytań

- Każde pytanie jest przetwarzane w pętli,
- Do historii wiadomości dodawany jest `SystemMessage`,
- Model generuje odpowiedź w oparciu o dokumenty i opcjonalnie uzupełnia brakującą wiedzę,
- Historia konwersacji jest przechowywana i może być czyszczona.

---

## Komponenty systemowe

### `Project`

Reprezentuje pojedynczy projekt:

- Atrybuty: `id`, `name`, `vector_store`, `loaded_docs`
- Obsługuje dodawanie dokumentów do wektorowej bazy danych

### `ProjectDB`

Warstwa pośrednicząca do bazy SQLite:

- Zarządza projektami i dokumentami
- Inicjalizuje tabele w bazie

### `history_manager`

Zarządza historią czatu użytkownika na poziomie projektu (identyfikowanego przez `thread_id`).

### `graph.invoke(...)`

Główna funkcja generująca odpowiedzi – wykorzystuje pipeline LangChaina i konfigurację RAG.

---

## Prompt Engineering

### `SYSTEM_PROMPT` & `SYSTEM_MESSAGE`

Określają zachowanie asystenta – odpowiedzi mają dwie sekcje:

- **Informacje z dokumentów**
- **Dodatkowe informacje**, jeśli potrzebne

### `GRADE_PROMPT`

Służy ocenie trafności dokumentu względem pytania – wynik to **tak** lub **nie**.

### `REWRITE_PROMPT`

Przeformułowuje pytanie użytkownika dla lepszego zrozumienia intencji.

---

## Konfiguracja i ścieżki

Konfiguracja `settings` zawiera m.in.:

- Ścieżkę do bazy danych: `DB_PATH`
- Ścieżkę do katalogu z dokumentami: `DATA_DIR_PATH`

---

## Uruchomienie

Punkt wejścia aplikacji:

```bash
just
```
