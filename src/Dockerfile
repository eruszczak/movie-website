FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

RUN apt-get update
RUN apt-get install gcc -y

COPY requirements.txt /code/

RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install gunicorn

WORKDIR /code/

COPY . /code/
