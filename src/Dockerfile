FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install gcc -y

RUN useradd --uid 1000 --create-home runner

USER 1000:1000

ENV PATH="/home/runner/.local/bin:${PATH}"

WORKDIR /code/

COPY --chown=1000:1000 requirements.txt /code/

RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY --chown=1000:1000 . /code/