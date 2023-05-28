# Database Final Project

[Live Demo](https://airline-ticket-system-production.up.railway.app/)

## Deploy with Docker Compose

Prerequisite:

- Ensure sure [docker-compose](https://docs.docker.com/compose/) is installed on your machine
- Make sure nothing is running on ports 3306 and 9999

Clone this repository and checkout to the `larry` branch

```bash
git clone https://github.com/larry-lime/airline-ticket-system
cd airline-ticket-system
git checkout larry
```

Run docker-compose

```bash
docker-compose up
```

Open http://localhost:9999 in your browser

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
