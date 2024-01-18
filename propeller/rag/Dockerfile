FROM python:3.10

COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
WORKDIR /opt
COPY . /opt
CMD ["python3", "/opt/retrievalserve.py"]

