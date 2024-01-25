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
    curl --location --request POST 'http://localhost:8000/langserve/invoke'     --header 'Content-Type: application/json'     --data-raw '{
        "input": "Tell me something about University of Arizona"
    }'
```

2. Calling the "Tell me a joke" route with "topic" as input

```
curl --location --request POST 'http://localhost:8000/joke/invoke'     --header 'Content-Type: application/json'     --data-raw '{
        "input": {
            "topic": "cats"
        }
    }'
```

## Docker

You will need to run ollama separately.

build
```
docker build -t cyverse/chatur-langserve -f Dockerfile.langserve .
```

run
```
ocker run -ti -p 8000:8000 cyverse/chatur-langserve
```

## Docker Compose

### No Vector Database or GPU

build and run
```
docker compose --file docker-compose.yml --project-name "chatur" build
docker compose --file docker-compose.yml --project-name "chatur" up -d
docker compose --file docker-compose.yml --project-name "chatur" exec ollama ollama pull mistral
```

### Vector Database in ./vectordb/RNR355; No GPU

build and run
```
docker compose --file docker-compose-vectordb.yml --project-name "chatur" build
docker compose --file docker-compose-vectordb.yml --project-name "chatur" up -d
docker compose --file docker-compose-vectordb.yml --project-name "chatur" exec ollama ollama pull mistral
```

### Vector Database in ./vectordb/RNR355; NVIDIA GPU

build and run
```
docker compose --file docker-compose-vectordb-gpu.yml --project-name "chatur" build
docker compose --file docker-compose-vectordb-gpu.yml --project-name "chatur" up -d
docker compose --file docker-compose-vectordb-gpu.yml --project-name "chatur" exec ollama ollama pull mistral
```
