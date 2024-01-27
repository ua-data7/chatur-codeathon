import argparse
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms.ollama import Ollama

from langchain.memory import ConversationBufferMemory
from langserve import add_routes
import sys
import os

from langserve import CustomUserType

from importlib import metadata
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from sse_starlette import EventSourceResponse

from langserve import APIHandler
from vectordb import VectorDB

parser = argparse.ArgumentParser(
    prog="langclient",
    description="serve LLM+RAG via langserve")

parser.add_argument("host", type=str, default="127.0.0.1", help="host for langserve to listen to, defualt 127.0.0.1")
parser.add_argument("port", type=int, default=8000, help="port for langserve to listen to, default 8000")
parser.add_argument("vectorstore", type=str, help="path to the directory of vector store")
parser.add_argument("ollama", type=str, default="http://localhost:11434", help="URL of ollama, default http://localhost:11434")
parser.add_argument("--ollama_key", type=str, help="api key to include in the header when talking to ollama api")
args = parser.parse_args()

print("vectorstore: %s, ollama_host: %s" % (args.vectorstore, args.ollama))


def format_documents(docs):
    out_docs = "\n".join(doc.page_content for doc in docs)
    print(out_docs)
    return out_docs

# Prompt
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Using the following documents, help answer questions as a teacher would help a student. Remember to only answer the question they asked: {context}"
    ),
    HumanMessagePromptTemplate.from_template("{question}"),
])


class Question(CustomUserType):
    question: str
    context: list

headers = {"Content-Type": "application/json"}
if args.ollama_key:
    headers["Authorization"] = "Bearer " + args.ollama_key
print(headers)
llm = Ollama(
    base_url=args.ollama,
    headers=headers,
    model="mistral",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

vectorstore = VectorDB(args.vectorstore)
retriever = vectorstore.as_retriever()

chain = (
    {"context": retriever | format_documents, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

add_routes(app, chain, path="/langserve")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


##########
# to use #
##########
### POST /langserve/invoke
### json params:
### {
###   "input": "User question goes here.",
###   "config": {},
###   "kwargs": {}
### }
