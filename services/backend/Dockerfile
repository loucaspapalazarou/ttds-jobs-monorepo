FROM python:3.9-slim-buster

LABEL version=0.2.2

ENV PYTHONUNBUFFERED True

RUN apt-get update && \
    apt-get -y install g++ && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/libc/gcc/aarch64-linux-gnu/8/cc1plus /usr/local/bin/

RUN mkdir app
ENV APP_HOME /app
WORKDIR $APP_HOME

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY services/backend/requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt

COPY services/backend/src/ ./backend

CMD exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}
