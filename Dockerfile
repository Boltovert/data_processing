FROM python:3.12.6-slim-bookworm

ENV PROJECT_ROOT=/app
ENV PYTHONPATH=$PROJECT_ROOT

RUN mkdir $PROJECT_ROOT/

WORKDIR $PROJECT_ROOT

RUN apt update && apt --fix-broken install -y && apt install -y make git rsync cron curl

RUN git config --global --add safe.directory /app/build

RUN python -m pip install poetry==1.8.3

COPY pyproject.toml poetry.lock $PROJECT_ROOT/

RUN poetry config virtualenvs.create false && poetry install --no-root

RUN mkdir /userfiles/

COPY . $PROJECT_ROOT
