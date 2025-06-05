from langchain.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów. \
         Jeżeli czegoś nie ma w dokumentach napisz że nie ma tej informacji w dostarczonych dokumentach. Natomiast jeżeli odpowiedź jest zawarta w dokumentach, \
         ale uważasz, że mógłbyś ją rozwinąć, to dodać możesz dodatkowe informacje, które mogą być przydatne dla studenta. "),
        ("human", "Pytanie: {question}"),
        ("human", "Kontekst: {context}")
    ]
)