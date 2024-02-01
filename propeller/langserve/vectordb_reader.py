# -*- coding: utf-8 -*-

"""This module holds the vector database maintenance logic."""

from typing import Optional

from langchain_community.embeddings import (
    GPT4AllEmbeddings
)

from langchain_community.vectorstores import Chroma   # pylint: disable=no-name-in-module
from langchain_core.vectorstores import VectorStoreRetriever

class VectorDBReader:
    """
    This class provide reader for a vector database, When constructing one, the path to the folder where the database
    will be persisted should be provided. If it isn't the database will not be
    persisted.
    """

    def __init__(self, db_path:Optional[str]=None):
        self._db_path = db_path
        self._impl = Chroma(embedding_function=GPT4AllEmbeddings(), persist_directory=db_path)

    def as_retriever(self) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore."""
        return self._impl.as_retriever()
