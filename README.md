# Database Final Project

## Deploy with Docker

Prerequisite:

- Ensure sure Docker is installed on your machine
- Make sure nothing is running on ports 8000 and 9999

Clone this repository

```bash
git clone https://github.com/larry-lime/airline-ticket-system
cd airline-ticket-system
```

Run docker compose

```bash
docker compose up -d --build
```

Open http://localhost:8000 in your browser

## Development

Create Python virtual environment

```bash
python3 -m venv .venv
```

Start virtual environment

```bash
. .venv/bin/activate
```

Install requirements

```bash
pip3 install -r requirements.txt
```

Initialize database

```bash
flask --app airline init-db
```

Start development server

```bash
flask --app airline run --debug
```
