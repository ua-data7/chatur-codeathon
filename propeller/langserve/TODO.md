# Make Ollama as a separate pod

From following doc
https://github.com/jmorganca/ollama/blob/main/docs/faq.md#how-can-i-expose-ollama-on-my-network

Ollama binds to 127.0.0.1 port 11434 by default. Change the bind address with the OLLAMA_HOST environment variable. Refer to the section above for how to use environment variables on your platform.

Access remote Ollama service
ollama_llm = Ollama(base_url="https://your_url:11434", model="llama2")





