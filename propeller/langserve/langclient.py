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

from langchain_core.runnables import RunnablePassthrough
from langserve import add_routes
from fastapi import FastAPI
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])


rag_runnable = RemoteRunnable("http://localhost:8000/")
llm_runnable = RemoteRunnable("http://localhost:8001/mistral/")



def format_documents(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Prompt
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "Using the following documents, help answer questions as a teacher would help a student. Remember to only answer the question they asked: {context}"
        ),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]
)
chain = {"context": rag_runnable | format_documents, "question": RunnablePassthrough()} | prompt| llm_runnable | StrOutputParser()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    chain,
    path="/rag",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)


# results = chain.invoke("Describe the three sides of the Fire Behavior Triangle?")

# print(results)
