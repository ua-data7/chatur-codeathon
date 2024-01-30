# -*- coding: utf-8 -*-

"""This module holds the vector database maintenance logic."""

import pathlib
import json
import os
import tempfile
from typing import Optional, Literal, List

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import (
    GPT4AllEmbeddings
)

from langchain_community.vectorstores import Chroma   # pylint: disable=no-name-in-module
from langchain_community.document_loaders import (
    PyPDFLoader,
    PDFMinerLoader,
    PyPDFium2Loader,
    PyMuPDFLoader,
    UnstructuredPowerPointLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader
)

from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_core.vectorstores import VectorStoreRetriever

import tiktoken
import pptx2md
from pptx2md.global_var import g as pptx2md_g
import mammoth
import pysbd


def _tiktoken_len(text) -> int:
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

        # this splits the input text
        self.text_splitter = RecursiveCharacterTextSplitter(
            # chunk size should not be very large as model has a limit
            chunk_size = 400,
            # this is a configurable value
            chunk_overlap = 200,
            length_function = _tiktoken_len,
        )

    def _dump_docs(self, docs:List[Document], doc_output_path:str) -> None:
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

    def _clean_doc(self, docs:List[Document], is_pdf:bool=False) -> List[Document]:
        new_docs = []
        for doc in docs:
            if hasattr(doc, "page_content") and len(doc.page_content) > 0:
                content = doc.page_content.replace("\n"," ")
                
                doctype = None
                clean = False
                if is_pdf:
                    doctype = "pdf"
                    clean = True

                seg=pysbd.Segmenter(language="en", doc_type=doctype, clean=clean)
                all_sent=seg.segment(content)
                page_content="\n".join(all_sent)

                if len(page_content) > 0:
                    new_doc = Document(page_content=page_content, metadata=doc.metadata.copy())
                    new_docs.append(new_doc)

        split_docs = self.text_splitter.split_documents(new_docs)
        self._make_doc_safe(split_docs)

        return split_docs

    def _make_doc_safe(self, docs:List[Document]) -> None:
        removed = []
        for doc in docs:
            self._make_meta_safe(doc)
            
            if not doc.page_content:
                # empty
                removed.append(doc)

        for doc in removed:
            docs.remove(doc)

    def _make_meta_safe(self, doc:Document) -> None:
        for k in doc.metadata:
            v = doc.metadata[k]
            if isinstance(v, dict):
                # is dict
                doc.metadata[k] = json.dumps(v)
            elif isinstance(v, list):
                # is array
                doc.metadata[k] = json.dumps(v)

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
            case ".pptx":
                self.add_pptx(path, doc_output_path)
            case ".ppt":
                self.add_ppt(path, doc_output_path)
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
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_pdf(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a PDF file to the vector store.

        Params:
          pdf_path  The path to the file on the local filesystem
        """

        """
        use one of these
        - _add_pdf_pypdf
        - _add_pdf_pdfminer
        - _add_pdf_pypdfium2
        - _add_pdf_pymupdf
        """
        return self._add_pdf_pypdf(pdf_path=pdf_path, doc_output_path=doc_output_path)
    
    def _add_pdf_pypdf(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        docs = PyPDFLoader(pdf_path).load_and_split()
        docs = self._clean_doc(docs, True)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_pdf_pdfminer(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        docs = PDFMinerLoader(pdf_path).load()
        docs = self._clean_doc(docs, True)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_pdf_pypdfium2(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        docs = PyPDFium2Loader(pdf_path).load()
        docs = self._clean_doc(docs, True)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_pdf_pymupdf(self, pdf_path:str, doc_output_path:Optional[str]) -> None:
        docs = PyMuPDFLoader(pdf_path).load()
        docs = self._clean_doc(docs, True)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_ppt(self, ppt_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a PowerPoint file to the vector store.

        Params:
          ppt_path  The path to the file on the local filesystem
        """
        docs = UnstructuredPowerPointLoader(ppt_path).load()
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_pptx(self, pptx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a PowerPoint file to the vector store.

        Params:
          pptx_path  The path to the file on the local filesystem
        """

        """
        use one of these
        - _add_pptx_pptx2md
        - _add_pptx_unstructured
        """
        return self._add_pptx_pptx2md(pptx_path=pptx_path, doc_output_path=doc_output_path)

    def _add_pptx_pptx2md(self, pptx_path:str, doc_output_path:Optional[str]) -> None:
        try:
            pptx2md_g.disable_image = True
            pptx2md_g.disable_wmf = True
            pptx2md_g.disable_color = True
            pptx2md_g.disable_escaping = True

            prs = pptx2md.Presentation(pptx=pptx_path)
            temp_path = tempfile.mktemp()
            md_out = pptx2md.outputter.md_outputter(temp_path)
            pptx2md.parse(prs, md_out)
            self.add_markdown(markdown_path=temp_path, doc_output_path=doc_output_path)

            os.remove(temp_path)
        except:
            # fail to convert to markdown
            self._add_pptx_unstructured(ppt_path=pptx_path, doc_output_path=doc_output_path)

    def _add_pptx_unstructured(self, ppt_path:str, doc_output_path:Optional[str]) -> None:
        docs = UnstructuredPowerPointLoader(ppt_path).load()
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_docx(self, docx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a Word file to the vector store.

        Params:
          docx_path  The path to the file on the local filesystem
        """
        
        """
        use one of these
        - _add_docx_docx2txt
        - _add_docx_mammoth (not reliable)
        """
        return self._add_docx_docx2txt(docx_path=docx_path, doc_output_path=doc_output_path)

    def _add_docx_docx2txt(self, docx_path:str, doc_output_path:Optional[str]) -> None:
        docs = Docx2txtLoader(docx_path).load()
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_docx_mammoth(self, docx_path:str, doc_output_path:Optional[str]) -> None:
        with open(docx_path, "rb") as docx_f:
            md_out = mammoth.convert_to_markdown(docx_f)
            
        temp_path = tempfile.mktemp()
        with open(temp_path, "w") as temp_f:
            temp_f.write(md_out.value)

        self.add_markdown(markdown_path=temp_path, doc_output_path=doc_output_path)

        os.remove(temp_path)

    def add_xlsx(self, xlsx_path:str, doc_output_path:Optional[str]) -> None:
        """
        Adds a Excel file to the vector store.

        Params:
          xlsx_path  The path to the file on the local filesystem
        """
        docs = UnstructuredExcelLoader(xlsx_path).load()
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def add_text(self, text:Literal, doc_output_path:Optional[str]) -> None:
        """
        Adds a block of text to the vector store.

        Params:
          text  the block of text
        """
        docs = self.text_splitter.create_documents([text])
        docs = self._clean_doc(docs, False)

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
        docs = self._clean_doc(docs, False)

        if doc_output_path:
            self._dump_docs(docs, doc_output_path)

        self._add_docs(docs)

    def _add_docs(self, docs) -> None:
        self._impl = Chroma.from_documents(
            documents=docs, embedding=self._impl.embeddings, persist_directory=self._db_path)

    def as_retriever(self) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore."""
        return self._impl.as_retriever()
