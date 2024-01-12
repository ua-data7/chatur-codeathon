FROM python:3

WORKDIR  /opt/langserve
COPY . .
RUN apt install -y gcc && \
    pip3 install -r requirements.txt

# Importing the OpenAI library requires an API key in this environment variable. This one is fake.
ENV OPENAI_API_KEY=notreal

ENTRYPOINT python3 /opt/langserve/llmserve2.py
