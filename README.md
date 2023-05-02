# Database Final Project

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

- [ ] Add icons to the frontend
- [ ] Have a form send you an email when a new user signs up
  - Use [Formspree](https://formspree.io/forms) potentially
- [ ] Add foreign currency support
- [ ] Ask use to use their current location

### Medium

- [ ] Add foreign language support. Auto translate everything?
- [ ] Add ability to login with third party services (Google, Facebook, etc.)

### Hard

- [ ] Add articles relavent to the airline industry and search history
  - [ ] Add a reccomentation system if possible
  - [ ] Reccomend them based on their search history
  - [ ] Does not need to use machine learning. It can simply use keywords
  - [ ] Alternatively, you can use some NLP library
