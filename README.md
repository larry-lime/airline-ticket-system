# Database Final Project

[Live Demo](https://airline-ticket-system-production.up.railway.app/) 

## Getting Started

1. Create Python virtual environment

```shell
python3 -m venv .venv
```

2. Start virtual environment

```shell
. .venv/bin/activate
```

1. Install requirements

```shell
pip3 install -r requirements.txt
```

## Development

1. Start python virtual environment:

```shell
. .venv/bin/activate
```

2. Initialize database

```shell
flask --app airline init-db
```

3. Start development server

```
flask --app airline run --debug
```

## TODOs

### Easy

- [ ] Use Plotly for data vis
  - [ ] [Plotly Tutorial](https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946) 
  - [ ] Use plotly to make a Geo map
- [ ] Add articles relavent to the airline industry
  - Sort (reccomend) articles based on purchase history
  - "Reccomend" articles based on destination_city
  - Write code to make requests to OpenAI api (test it if we have tokens)
  - Allow airline staff to do this stuff
- [ ] Add icons to the frontend
- [ ] Have a form send you an email when a new user signs up
  - Use [Formspree](https://formspree.io/forms) potentially
  - Send an email for ticket purchase
- [ ] Add foreign currency support
- [ ] Ask use to use their current location

### Medium

- [ ] Generate articles based on airport locations
- [ ] Add foreign language support. Auto translate everything?
- [ ] Add ability to login with third party services (Google, Facebook, etc.)

### Hard

- [ ] Add a reccomentation system for articles
  - [ ] Reccomend them based on their flight purchases (and search history if you want to store that)
  - [ ] Does not need to use machine learning. It can simply use keywords
  - [ ] Alternatively, you can use some NLP library
