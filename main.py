import torch

from rag_pipeline import RAGPipeline

def main():
    print(torch.cuda.is_available())
    print("=== Asystent Nauki RAG ===")
    rag = RAGPipeline()
    rag.load_documents()

    docs = rag.retriever.get_relevant_documents("Co definiuje standard 802.1Q?")
    print(docs)

    while True:
        question = input("\nPytanie (lub wpisz 'exit'): ")
        if question.lower() == 'exit':
            break
        answer = rag.ask_question(question)
        print("\n🧠 Odpowiedź:\n", answer)


if __name__ == "__main__":
    main()
