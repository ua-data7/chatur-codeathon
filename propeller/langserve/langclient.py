
from langserve import RemoteRunnable

from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama

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

HOST = sys.argv[1]
PORT = int(sys.argv[2])
VECTORSTORE = sys.argv[3]

print("vectorstore: {}".format(VECTORSTORE))

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


llm = Ollama(
    model="mistral",
)

vectorstore = VectorDB(VECTORSTORE)
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

    uvicorn.run(app, host=HOST, port=PORT)


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
