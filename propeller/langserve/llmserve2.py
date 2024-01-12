#!/usr/bin/env python
"""langserve that serves up our LLMs"""
import os
from fastapi import FastAPI
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from langserve import add_routes
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

openai_key = os.getenv("OPENAI_API_KEY")

add_routes(
    app,
    ChatOpenAI(model="Mistral-7B-OpenOrca", openai_api_key=openai_key, base_url="https://chatur-api.cyverse.ai/v1/"),
    path="/mistral",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)