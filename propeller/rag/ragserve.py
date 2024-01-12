#!/usr/bin/env python
"""Serves up the local RAG via langserve."""
from fastapi import FastAPI
from langserve import add_routes
from vectordb import VectorDB
import sys

VECTORPATH = sys.argv[1]
RAGHOST = sys.argv[2]
RAGPORT = int(sys.argv[3])

vectorstore = VectorDB(VECTORPATH)
retriever = vectorstore.as_retriever()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Simple API to serve up the RAG",
)
# Adds routes to the app for using the retriever under:
# /invoke
# /batch
# /stream
add_routes(app, retriever)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=RAGHOST, port=RAGPORT)
