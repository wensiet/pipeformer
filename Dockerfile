FROM python:latest

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install -v

ENTRYPOINT ["/usr/bin/sh"]
