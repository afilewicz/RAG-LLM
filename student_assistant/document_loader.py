from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.parsers.images import RapidOCRBlobParser
from pathlib import Path
from itertools import chain

import asyncio

from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger


logger = get_logger(__name__)


async def load_and_chunk_docs():
    data_path = Path(settings.DATA_DIR_PATH)
    tasks = []

    for file in data_path.glob("*"):
        if file.suffix in {".pdf"}:
            tasks.append(load_and_chunk_pdf(file.name))

    loaded_docs = await asyncio.gather(*tasks)

    return list(chain.from_iterable(loaded_docs))


async def load_and_chunk_pdf(file_name: str):
    loader = PyPDFLoader(
        f"{settings.DATA_DIR_PATH}/{file_name}", 
        extract_images=True,
        images_inner_format="mardkdown-img",
        images_parser=RapidOCRBlobParser()
    )

    pages = [page async for page in loader.alazy_load()]

    logger.info(f"Loaded {len(pages)} pages from {file_name}.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)
    pages = text_splitter.split_documents(pages)
    
    logger.info(f"Split {file_name} into {len(pages)} chunks.")
    return pages