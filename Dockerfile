FROM python:3.9.0b1-alpine3.11
LABEL maintainer="Piotr Kawa"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D recipeapiuser
USER recipeapiuser