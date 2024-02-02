from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama

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
from vectordb_reader import VectorDBReader

from langchain.globals import set_debug

set_debug(True) # Comment out to remove debug messages

HOST = sys.argv[1]
PORT = int(sys.argv[2])
VECTORSTORE = sys.argv[3]
OLLAMA_HOST = sys.argv[4]

print("vectorstore: %s, ollama_host: %s" % (VECTORSTORE, OLLAMA_HOST))


def format_documents(docs):
    """"""
    out_docs = "\n\n".join(f"Text: {doc.page_content}\nSource: {doc.metadata['source']}, page {doc.metadata['page']}" for doc in docs)
    return out_docs


prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """"You are a teaching assistant. Answer the student's question using information only and only from the text fields of the documents included in the context that is between triple quotes. When you answer the question, quote the text that you used to base your answer off and state its source, which is also part of the document in the context. If you can't answer it, then say “I can't answer this question”.

        For example. If a context document is:

        Text: Further, these experiences must be delivered in a context that encourages the young person to drive goal setting and achievement, as opposed to learning trajectories defined by others (Olenik, 2017).
        Source: /papers/az1900-2021.pdf, page 2

        And the question is: "How must the experiences be delivered?", you will phrase the answer and state that you did from information that originates from page 2 of the file named /papers/az1900-2021.pdf.
        
        Context: 
        ```{context}```"""
    ),
    HumanMessagePromptTemplate.from_template("Question: {question}"),
])


class Question(CustomUserType):
    question: str
    context: list


llm = ChatOllama(
    base_url="http://%s:11434" % OLLAMA_HOST,
    model="mixtral",
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

vectorstore = VectorDBReader(VECTORSTORE)
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

# chain.invoke("Hello")

x = 0
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
