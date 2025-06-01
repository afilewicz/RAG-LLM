from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from embeddings import get_embedding_model
from document_loader import load_and_chunk_docs
from config import MODEL_NAME, CHROMA_PATH
from langchain_openai import ChatOpenAI
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class RAGPipeline:
    def __init__(self):
        self.db = None
        self.retriever = None
        self.qa_chain = None

    def load_documents(self):
        print("📚 Ładowanie dokumentów i tworzenie bazy wektorowej...")
        chunks = load_and_chunk_docs()
        embed_model = get_embedding_model()
        print(f"📦 chunks: {len(chunks)}")
        print(f"🧩 Przykład chunku: {chunks[0] if chunks else 'BRAK'}")
        self.db = Chroma.from_documents(chunks, embed_model, persist_directory=CHROMA_PATH)
        # self.db.persist()
        self.retriever = self.db.as_retriever()
        llm = ChatOpenAI(
            model=MODEL_NAME,
            openai_api_key=OPENAI_API_KEY,
            temperature=0.2,
            max_tokens=512
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=self.retriever,
            return_source_documents=False
        )

    def ask_question(self, question: str) -> str:
        return self.qa_chain.invoke(question)
