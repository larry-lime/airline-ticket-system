# syntax=docker/dockerfile:1

FROM python:3.11.3-bullseye

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD [ "flask", "--app", "airline", "run", "--host=0.0.0.0", "--port=8000", "--debug" ]
