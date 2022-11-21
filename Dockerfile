# Sample docker file for the application
FROM python:3.9-alpine3.15

RUN apk add --no-cache postgresql-libs && \
apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN apk add git
RUN apk add python3-dev build-base linux-headers pcre-dev
RUN python -m pip install pip

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN ["pip", "install", "--upgrade", "pip"]

COPY requirements.txt /usr/src/app/
RUN ["pip", "install", "--no-cache-dir", "-r", "requirements.txt"]
RUN apk --purge del .build-deps

COPY . /usr/src/app

ENV PORT 7042
EXPOSE 7042

WORKDIR /usr/src/app

CMD ["uwsgi", "--yaml", "webapp/conf/env/uwsgi.yaml", "--http-socket", "0.0.0.0:7042"]
