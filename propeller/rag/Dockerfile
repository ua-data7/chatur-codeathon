FROM python:3.10

COPY ./*.py /opt
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
CMD ["python3", "/opt/ragserve.py"]

