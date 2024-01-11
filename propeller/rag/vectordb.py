from typing import Optional, List, Literal
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import TextLoader

import tiktoken
import pathlib

def _tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)


def create(docs:List[Document], persist_db_path:Optional[str]=None) -> Chroma:
    # store it into vector store (chroma) using gpt4all embeddings
    return Chroma.from_documents(
        documents=docs,
        embedding=GPT4AllEmbeddings(),
        persist_directory=persist_db_path)


# this splits the input text
text_splitter = RecursiveCharacterTextSplitter(
    # chunk size should not be very large as model has a limit
    chunk_size = 1000,
    # this is a configurable value
    chunk_overlap = 200,
    length_function = _tiktoken_len,
)

def create_from_text(text:Literal) -> Chroma:
    # chunk input into multiple documents
    docs = text_splitter.create_documents([text])
    return create(docs)

def create_from_text_file(text_path:str) -> Chroma:
    loader = TextLoader(text_path)
    docs = loader.load()
    return create(docs)

def create_from_pdf(pdf_path:str) -> Chroma:
    loader = PyPDFLoader(pdf_path)
    docs = loader.load_and_split()
    return create(docs)

def create_from_markdown(markdown_path:str) -> Chroma:
    loader = UnstructuredMarkdownLoader(markdown_path)
    docs = loader.load()
    return create(docs)

def create_from_pptx(pptx_path:str) -> Chroma:
    loader = UnstructuredPowerPointLoader(pptx_path)
    docs = loader.load()
    return create(docs)

def create_from_file(path:str) -> Chroma:
    # detect format
    file_ext = pathlib.Path(path).suffix
    match str.lower(file_ext):
        case ".pdf":
            return create_from_pdf(path)
        case ".md":
            return create_from_markdown(path)
        case ".pptx":
            return create_from_pptx(path)
        case _:
            return create_from_text_file(path)
        
def load(persist_db_path:str) -> Chroma:
    return Chroma(embedding_function=GPT4AllEmbeddings(), persist_directory=persist_db_path)
