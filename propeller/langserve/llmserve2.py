#!/usr/bin/env python
"""langserve that serves up our LLMs"""
import argparse
import os
from fastapi import FastAPI
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from langserve import add_routes
import sys


def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="The IP address of the interface to listen to.",
        default="0.0.0.0"
    )
    parser.add_argument(
        "--port",
        help="The port number to listen to.",
        default=8000,
        type=int
    )
    return parser.parse_args()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

#openai_key = os.getenv("OPENAI_API_KEY")

"""
add_routes(
    app,
    ChatOpenAI(model="Mistral-7B-OpenOrca", openai_api_key=openai_key, base_url="https://chatur-api.cyverse.ai/v1/"),
    path="/mistral",
)
"""

add_routes(
    app,
    ChatOpenAI(model="Mistral-7B-OpenOrca", base_url="http://chatur-api-server/v1"),
    path="/mistral",
)

if __name__ == "__main__":
    import uvicorn
    args = parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
