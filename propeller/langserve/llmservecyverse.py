#!/usr/bin/env python
import os
from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langserve import add_routes

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

openai_key = os.getenv("OPENAI_API_KEY")

add_routes(
    app,
    ChatOpenAI(model="Mistral-7B-OpenOrca", openai_api_key=openai_key, base_url="https://chatur-api.cyverse.ai/v1/"),
    path="/fastchat",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8008)