from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.parsers.images import RapidOCRBlobParser
from pathlib import Path
from itertools import chain

import asyncio
import io
import contextlib
import shutil

from student_assistant.core.config import settings
from student_assistant.core.logging import get_logger


logger = get_logger(__name__)


async def load_and_chunk_docs(project_name: str):
    data_path = Path(settings.DATA_DIR_PATH)
    tasks = []
    file_names = []
    files_to_move = []

    for file in data_path.glob("*"):
        if file.suffix == ".pdf":
            tasks.append(load_and_chunk_pdf(file.name))
            file_names.append(file.name)
            files_to_move.append(file)

    loaded_docs = await asyncio.gather(*tasks)

    target_dir = Path(f"loaded_docs/{project_name}")
    target_dir.mkdir(parents=True, exist_ok=True)

    for file in files_to_move:
        shutil.move(str(file), str(target_dir / file.name))

    return list(chain.from_iterable(loaded_docs)), file_names

class SafeRapidOCRBlobParser(RapidOCRBlobParser):
    def extract_images_from_page(self, page):
        try:
            return super().extract_images_from_page(page)
        except Exception as e:
            logger.warning(f"Error extracting images from page {page.page_number}: {e}")
            return []

async def load_and_chunk_pdf(file_name: str):
    loader = PyPDFLoader(
        f"{settings.DATA_DIR_PATH}/{file_name}", 
        extract_images=True,
        images_inner_format="markdown-img",
        images_parser=SafeRapidOCRBlobParser()
    )

    with contextlib.redirect_stderr(io.StringIO()):
        pages = []
        agen = loader.alazy_load()
        while True:
            try:
                page = await agen.__anext__()
            except StopAsyncIteration:
                break
            except Exception as e:
                logger.warning(f"Error loading page: {e}")
                continue
            pages.append(page)

    logger.info(f"Loaded {len(pages)} pages from {file_name}.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)
    pages = text_splitter.split_documents(pages)
    
    logger.info(f"Split {file_name} into {len(pages)} chunks.")
    return pages

async def load_and_chunk_website(url: str):
    loader = WebBaseLoader(url)

    with contextlib.redirect_stderr(io.StringIO()):
        pages = [page async for page in loader.alazy_load()]

    logger.info(f"Loaded {len(pages)} pages from {url}.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)
    pages = text_splitter.split_documents(pages)

    logger.info(f"Split {url} into {len(pages)} chunks.")
    return pages