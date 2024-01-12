# LangChain LangServe

setup LangChain LangServe

Prerequisite:
Python 3+ installation

Install Packages:

`pip install -r requirements.txt`

Setup Key:

`export OPENAI_API_KEY=ADD_KEY_HERE`

Run Server:

`python3 ./server.py`

Usage:

1. Calling OpenAI's Q/A API

```
    curl --location --request POST 'http://localhost:8000/openai/invoke'     --header 'Content-Type: application/json'     --data-raw '{
        "input": "Tell me something about University of Arizona"
    }'
```

2. Calling the "Tell me a joke" route with "topic" as input

```
url --location --request POST 'http://localhost:8000/joke/invoke'     --header 'Content-Type: application/json'     --data-raw '{
        "input": {
            "topic": "cats"
        }
    }'
```
