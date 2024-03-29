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
from vectordb_reader import VectorDBReader

from langchain.globals import set_debug

set_debug(True) # Comment out to remove debug messages

HOST = sys.argv[1]
PORT = int(sys.argv[2])
VECTORSTORE = sys.argv[3]
COLLECTION = sys.argv[4]
OLLAMA_HOST = sys.argv[5]
MODEL = sys.argv[6]

print("vectorstore: %s, ollama_host: %s" % (VECTORSTORE, OLLAMA_HOST))


def format_documents(docs):
    out_docs = "\n".join(doc.page_content for doc in docs)
    print(out_docs)
    return out_docs

"""You are a teaching assistant. Answer the student's question using information only and only from the context passage that is between triple quotes. When you answer the question, quote the text that you used to base your answer off. If you can't answer it, then say “I can't answer this question”.Context:
```"""

# Prompt
# prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template(
#         "Using the following documents, help answer questions as a teacher would help a student. Remember to only answer the question they asked: {context}"
#     ),
#     HumanMessagePromptTemplate.from_template("{question}"),
# ])

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        """"You are a teaching assistant. Answer the student's question using information only and only from the context passage that is between triple quotes. When you answer the question, quote the text that you used to base your answer off. If you can't answer it, then say “I can't answer this question”.

        Context:
        ```{context}```"""
    ),
    HumanMessagePromptTemplate.from_template("Question: {question}"),
])


class Question(CustomUserType):
    question: str
    context: list


llm = Ollama(
    base_url="http://%s:11434" % OLLAMA_HOST,
    model=MODEL,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

vectorstore = VectorDBReader(db_path=VECTORSTORE, collection_name=COLLECTION)
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
