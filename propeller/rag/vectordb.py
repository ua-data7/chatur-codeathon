from typing import Optional, List, Literal
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
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

class VectorDB:

    def __init__(self, db_path:Optional[str]):
        self._db_path = db_path
        self._impl = Chroma(embedding_function=GPT4AllEmbeddings(), persist_directory=db_path)

    def add_docs(self, docs:List[Document]) -> None:
        self._impl = Chroma.from_documents(
            documents=docs, embedding=self._impl.embeddings, persist_directory=self._db_path)

    def add_file(self, path:str) -> None:
        # detect format
        file_ext = pathlib.Path(path).suffix
        match str.lower(file_ext):
            case ".pdf":
                self.add_pdf(path)
            case ".md":
                self.add_markdown(path)
            case ".pptx":
                self.add_pptx(path)
            case _:
                self.add_text_file(path)

    def add_markdown(self, markdown_path:str) -> None:
        self.add_docs(UnstructuredMarkdownLoader(markdown_path).load())

    def add_pdf(self, pdf_path:str) -> None:
        self.add_docs(PyPDFLoader(pdf_path).load_and_split())

    def add_pptx(self, pptx_path:str) -> None:
        self.add_docs(UnstructuredPowerPointLoader(pptx_path).load())

    def add_text(self, text:Literal) -> None:
        # this splits the input text
        text_splitter = RecursiveCharacterTextSplitter(
            # chunk size should not be very large as model has a limit
            chunk_size = 1000,
            # this is a configurable value
            chunk_overlap = 200,
            length_function = _tiktoken_len,
        )
        # chunk input into multiple documents
        self.add_docs(text_splitter.create_documents([text]))

    def add_text_file(self, text_path:str) -> None:
        self.add_docs(TextLoader(text_path).load())

    def as_retriever(self) -> VectorStoreRetriever:
        return self._impl.as_retriever()
