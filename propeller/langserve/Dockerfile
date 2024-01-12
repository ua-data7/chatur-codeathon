FROM python:3

WORKDIR  /opt/langserve
COPY . .
RUN apt install -y gcc && \
    pip3 install -r requirements.txt
ENTRYPOINT python3 /opt/langserve/server.py
