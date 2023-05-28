# syntax=docker/dockerfile:1

FROM python:3.11.3-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "flask", "--app", "airline", "run", "--host=0.0.0.0" ]
