# -*- coding: utf-8 -*-

"""This module holds the vector database maintenance logic."""

import pathlib
from typing import Optional, Literal

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma   # pylint: disable=no-name-in-module
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.vectorstores import VectorStoreRetriever

import tiktoken

def _tiktoken_len(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

class VectorDB:
    """
    This class manages the maintenance of a vector database, e.g., adding
    documents. When constructing one, the path to the folder where the database
    will be persisted should be provided. If it isn't the database will not be
    persisted.
    """

    def __init__(self, db_path:Optional[str]):
        self._db_path = db_path
        self._impl = Chroma(embedding_function=GPT4AllEmbeddings(), persist_directory=db_path)

    def add_file(self, path:str) -> None:
        """
        Adds a file to the vector store. It will use the file's extension to
        determine the type of file.

        Params:
          path  The path to the file on the local filesystem
        """
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
        """
        Adds a markdown file to the vector store.

        Params:
          path  The path to the file on the local filesystem
        """
        self._add_docs(UnstructuredMarkdownLoader(markdown_path).load())

    def add_pdf(self, pdf_path:str) -> None:
        """
        Adds a PDF file to the vector store.

        Params:
          path  The path to the file on the local filesystem
        """
        self._add_docs(PyPDFLoader(pdf_path).load_and_split())

    def add_pptx(self, pptx_path:str) -> None:
        """
        Adds a PowerPoint file to the vector store.

        Params:
          path  The path to the file on the local filesystem
        """
        self._add_docs(UnstructuredPowerPointLoader(pptx_path).load())

    def add_text(self, text:Literal) -> None:
        """
        Adds a block of text to the vector store.

        Params:
          text  the block of text
        """
        # this splits the input text
        text_splitter = RecursiveCharacterTextSplitter(
            # chunk size should not be very large as model has a limit
            chunk_size = 1000,
            # this is a configurable value
            chunk_overlap = 200,
            length_function = _tiktoken_len,
        )
        # chunk input into multiple documents
        self._add_docs(text_splitter.create_documents([text]))

    def add_text_file(self, text_path:str) -> None:
        """
        Adds a text file of unknown type to the vector store.

        Params:
          path  The path to the file on the local filesystem
        """
        self._add_docs(TextLoader(text_path).load())

    def _add_docs(self, docs):
        self._impl = Chroma.from_documents(
            documents=docs, embedding=self._impl.embeddings, persist_directory=self._db_path)

    def as_retriever(self) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore."""
        return self._impl.as_retriever()
