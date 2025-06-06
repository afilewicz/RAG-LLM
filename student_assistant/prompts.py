from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage


SYSTEM_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów.\
         Rozdziel wyraźnie odpowiedź na dwie sekcje: \n \
                   - informację tylko z dokumentów \n \
                   - jeśli informacje były niepełne, sekcję z twoimi informacjami."),
        ("human", "Pytanie: {question}"),
        ("human", "Kontekst: {context}")
    ]
)

GRADE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Jesteś oceniającym, który sprawdza trafność odnalezionego dokumentu względem pytania użytkownika.\n"
                "Oto odnaleziony dokument:\n\n{context}\n\n"
                "Oto pytanie użytkownika: {question}\n"
                "Jeśli dokument zawiera słowo kluczowe lub znaczenie semantyczne powiązane z pytaniem, oceń go jako trafny.\n"
                "Podaj binarną ocenę 'tak' lub 'nie', aby wskazać, czy dokument jest trafny względem pytania."
            )
        )
    ]
)

SYSTEM_MESSAGE = SystemMessage(
    content="Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów.\
         Rozdziel wyraźnie odpowiedź na dwie sekcje: \n \
                   - informację tylko z dokumentów \n \
                   - jeśli informacje były niepełne, sekcję z twoimi informacjami."
)

REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "user",
            (
                "Spójrz na podane pytanie i postaraj się zrozumieć jego ukryty semantyczny cel lub znaczenie.\n"
                "Oto oryginalne pytanie:"
                "\n ------- \n"
                "{question}"
                "\n ------- \n"
                "Sformułuj ulepszone pytanie:"
            )
        )
    ]
)