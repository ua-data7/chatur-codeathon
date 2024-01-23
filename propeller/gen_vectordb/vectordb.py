# -*- coding: utf-8 -*-

"""This module holds the vector database maintenance logic."""

import pathlib
import json
import os
from typing import Optional, Literal, List

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import Chroma   # pylint: disable=no-name-in-module
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader
)

from langchain.text_splitter import MarkdownHeaderTextSplitter
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

    def _dump_docs(self, docs:List[Document], doc_output_path:str):
        docdir = os.path.dirname(doc_output_path)
        os.makedirs(docdir, exist_ok=True)

        with open(doc_output_path, "w") as f:
                for docid, doc in enumerate(docs):
                    f.write("==== doc %d ====\n" % docid)
                    f.write("[metadata]\n")
                    f.write(json.dumps(doc.metadata))
                    f.write("\n\n")
                    f.write("[content]\n")
                    f.write(doc.page_content)
                    f.write("\n\n")

    def _make_doc_safe(self, docs:List[Document]):
        removed = []
        for doc in docs:
            self._make_meta_safe(doc)
            if not doc.page_content:
                # empty
                removed.append(doc)

        for doc in removed:
            docs.remove(doc)

    def _make_meta_safe(self, doc:Document):
        for k in doc.metadata:
            v = doc.metadata[k]
            if isinstance(v, list):
                # is array
                doc.metadata[k] = ", ".join(v)

    def add_file(self, path:str, doc_output_path:Optional[str]=None) -> None:
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
                self.add_pdf(path, doc_output_path)
            case ".md":
                self.add_markdown(path, doc_output_path)
            case ".pptx" | ".ppt":
                self.add_pptx(path, doc_output_path)
            case ".docx" | ".doc":
                self.add_docx(path, doc_output_path)
            case ".xlsx" | ".xls":
                #self.add_xlsx(path, doc_output_path)
                print("ignore microsoft excel file (%s)" % path)
            case ".png" | ".jpg" | ".jpeg" | ".gif" | ".tiff":
                print("ignore image file (%s)" % path)
            case ".txt":
                self.add_text_file(path, doc_output_path)
            case _:
                print("ignore unknown file (%s)" % path)

    def add_markdown(self, markdown_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a markdown file to the vector store.

        Params:
          markdown_path  The path to the file on the local filesystem
        """
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        filecontent = pathlib.Path(markdown_path).read_text()

        docs = markdown_splitter.split_text(filecontent)
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_pdf(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a PDF file to the vector store.

        Params:
          pdf_path  The path to the file on the local filesystem
        """
        docs = PyPDFLoader(pdf_path).load_and_split()
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_pptx(self, pptx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a PowerPoint file to the vector store.

        Params:
          pptx_path  The path to the file on the local filesystem
        """
        docs = UnstructuredPowerPointLoader(pptx_path, mode="elements").load()
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_docx(self, docx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a Word file to the vector store.

        Params:
          docx_path  The path to the file on the local filesystem
        """
        docs = Docx2txtLoader(docx_path).load()
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_xlsx(self, xlsx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a Excel file to the vector store.

        Params:
          xlsx_path  The path to the file on the local filesystem
        """
        docs = UnstructuredExcelLoader(xlsx_path).load()
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_text(self, text:Literal, doc_output_path:Optional[str]) -> None:
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

        docs = text_splitter.create_documents([text])
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_text_file(self, text_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a text file of unknown type to the vector store.

        Params:
          text_path  The path to the file on the local filesystem
        """
        docs = TextLoader(text_path).load()
        self._make_doc_safe(docs)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_docs(self, docs):
        self._impl = Chroma.from_documents(
            documents=docs, embedding=self._impl.embeddings, persist_directory=self._db_path)

    def as_retriever(self) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore."""
        return self._impl.as_retriever()
