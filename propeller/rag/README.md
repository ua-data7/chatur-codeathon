# langchain rag
setup langchain rag


```
pip install -r requirements.txt
```


Requires Ollama and Mistral model

Run ollama locally in docker
```
docker run -d -p 11434:11434 ollama/ollama --name ollama_cyverse
```

Download mistral model
```
docker exec ollama_cyverse ollama pull mistral
```


Run
```
python3 ./test_chat.py
```