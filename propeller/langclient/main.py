import os
import httpx

from fastapi import FastAPI
from fastapi import HTTPException


# load env / defaults
LLM_PROTO = os.getenv("LLM_PROTO", "http")
LLM_HOST = os.getenv("LLM_HOST", "localhost")
LLM_PORT = os.getenv("LLM_PORT", 8080)
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "v1")

llm_url = f"{LLM_PROTO}://{LLM_HOST}:{LLM_PORT}/{LLM_ENDPOINT}/"


## Our API handler
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)


async def call_llm_service(text:str):
    payload = {"text": text}
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer SOMEKEYGOESHERE",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(llm_url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception("Error calling LLM!")
    
    return response.json()


@app.post("/mistral")
async def process_text(data: str):
    try:
        response = await call_llm_service(data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
