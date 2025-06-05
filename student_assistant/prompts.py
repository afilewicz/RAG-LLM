from langchain.prompts import ChatPromptTemplate


SYSTEM_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów. \
         Jeżeli czegoś nie ma w dokumentach napisz że nie ma tej informacji w dostarczonych dokumentach. Natomiast jeżeli odpowiedź jest zawarta w dokumentach, \
         ale uważasz, że mógłbyś ją rozwinąć, to dodać możesz dodatkowe informacje, które mogą być przydatne dla studenta. "),
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