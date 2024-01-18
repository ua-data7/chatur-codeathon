"""
This runs langserve with fastapi to serve a REST api that expose the chain (RAG + LLM).

Environment variables:
LLM_MODEL_NAME: name of the LLM model to use
OPENAI_API_URL: url of the openai api

"""
from langserve import add_routes
from langserve import CustomUserType

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
# from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from fastapi import FastAPI

from vectordb import VectorDB

import sys
import os

# Host and port for fastapi to listen to
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


# llm = Ollama(
#     model="mistral",
# )
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "Mistral-7B-OpenOrca")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "http://chatur-api-server/v1")
llm = ChatOpenAI(model=LLM_MODEL_NAME, base_url=OPENAI_API_URL)

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
