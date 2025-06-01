from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path

def load_and_chunk_docs():
    data_path = Path("data")
    loaders = []

    for file in data_path.glob("*"):
        if file.suffix == ".txt":
            loaders.append(TextLoader(str(file)))
        elif file.suffix == ".pdf":
            loaders.append(PyPDFLoader(str(file)))

    docs = []
    for loader in loaders:
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)
