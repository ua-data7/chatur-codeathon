# -*- coding: utf-8 -*-

import os
from os import path
import re
import sys
from sys import stderr, stdin, stdout

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader)
from langchain_community.retrievers import TFIDFRetriever

from pptx.exc import PackageNotFoundError


def _mk_doc_loader(file_ext):
    match str.lower(file_ext):
        case ".docx":
            return Docx2txtLoader
        case ".pdf":
            # return UnstructuredPDFLoader
            # return PyPDFLoader
            return PDFMinerLoader
        case ".ppt":
            return UnstructuredPowerPointLoader
        case ".pptx":
            return UnstructuredPowerPointLoader
        case ".xls":
            return UnstructuredExcelLoader
        case ".xlsx":
            return UnstructuredExcelLoader
        case _:
            return TextLoader


def _ingest_docs(docs_dir):
    all_doc_parts = []

    for (doc_dir, _, doc_names) in os.walk(docs_dir):
        for doc_name in doc_names:
            doc_path = path.join(doc_dir, doc_name)
            (_, doc_ext) = path.splitext(doc_name)
            stderr.write(f"Ingesting {doc_path}\n")

            try:
                all_doc_parts += _mk_doc_loader(doc_ext)(doc_path).load_and_split()
            except PackageNotFoundError as e:
                stderr.write(f"\t{e}\n")

    retriever = TFIDFRetriever.from_documents(all_doc_parts)
    stderr.write("Finished ingesting documents\n")
    return retriever


def _read_prompt():
    try:
        return input()
    except EOFError:
        return ""


def _get_resp(tf_idf, prompt):
    docs = tf_idf.get_relevant_documents(prompt)
    resp = docs[0].page_content
    fmt_resp = re.sub("\n", "\n> ", re.sub("\n( ?\n)+", "\n\n", re.sub("[ \t]+", " ", resp)))
    metadata = docs[0].metadata
    return fmt_resp, metadata


def _main(argv):
    docs_dir = argv[1]
    tf_idf = _ingest_docs(docs_dir)
    stdout.write("# TF-IDF Baseline Prompts\n")

    while True:
        stdout.write("\n## PROMPT: ")
        prompt = _read_prompt()

        if not prompt:
            return

        if not stdin.isatty():
            stdout.write(f"_{prompt}_\n")

        resp, metadata = _get_resp(tf_idf, prompt)
        stdout.write(f"\n### RESPONSE\n> {resp}\n\n### METADATA: {metadata}\n")


if __name__ == '__main__':
    _main(sys.argv)
