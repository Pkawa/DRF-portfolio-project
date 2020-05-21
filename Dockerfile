FROM python:3.8-alpine
LABEL maintainer="Piotr Kawa"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-dependencies \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-dependencies

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D recipeapiuser
USER recipeapiuser