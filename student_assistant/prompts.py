from langchain.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Jesteś pomocnym asystentem studenta. Odpowiadasz na jego pytania wykorzystując wyciągnięte informacje z dokumentów."),
        ("human", "Pytanie: {question}"),
        ("human", "Kontekst: {context}")
    ]
)