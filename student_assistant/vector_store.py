from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from student_assistant.core.config import settings


embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)

vector_store = Chroma(
    collection_name="student_assistant",
    persist_directory=settings.CHROMA_PATH,
    embedding_function=embeddings
)