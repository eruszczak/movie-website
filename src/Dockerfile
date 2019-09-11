FROM nikolaik/python-nodejs:python3.7-nodejs8
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install gunicorn

WORKDIR /code/static

COPY static/package.json /code/static
COPY static/semantic.json /code/static
RUN npm install

WORKDIR /code/

COPY . /code/
