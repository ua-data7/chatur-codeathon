FROM python:3

ARG LLM_PROTO='http'
ARG LLM_HOST='https://chatur-api.cyverse.ai'
ARG LLM_PORT=''
ARG LLM_ENDPOINT='/v1/'

WORKDIR  /opt/langclient
COPY . .
RUN apt install -y gcc && \
    pip3 install -r requirements.txt
ENTRYPOINT uvicorn main:app --host localhost --port 8080 --reload
