# -*- coding: utf-8 -*-

"""This module holds the vector database maintenance logic."""

from typing import Optional

from langchain_community.embeddings import (
    GPT4AllEmbeddings
)

from langchain_community.vectorstores import Chroma   # pylint: disable=no-name-in-module
from langchain_core.vectorstores import VectorStoreRetriever
import chromadb

class VectorDBReader:
    """
    This class provide reader for a vector database, When constructing one, the path to the folder where the database
    will be persisted should be provided. If it isn't the database will not be
    persisted.
    """

    def __init__(self, db_path:Optional[str]=None, collection_name:Optional[str]=None):
        self._embedding=GPT4AllEmbeddings()
        self._db_path = db_path
        if collection_name:
            self._collection_name=collection_name
        else:
            self._collection_name="langchain"

        client_settings = chromadb.Settings()
        if db_path:
            client_settings.persist_directory=db_path
            client_settings.is_persistent=True

        client = chromadb.Client(client_settings)
        
        self._impl = Chroma(
            embedding_function=self._embedding, 
            client_settings=client_settings,
            client=client,
            collection_name=self._collection_name, 
        )

    def as_retriever(self) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore."""
        return self._impl.as_retriever()
