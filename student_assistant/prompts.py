from langchain.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów. Jeżeli czegoś nie ma w dokumentach napisz że nie ma tej informacji w dostarczonych dokumentach."),
        ("human", "Pytanie: {question}"),
        ("human", "Kontekst: {context}")
    ]
)