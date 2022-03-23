# Fastapi Demo Project


## Install requirements
* Create python environment
```bash
python3.8 -m venv venv
```


* Install requirements
```bash
pip install -r requirements.txt
```


## Setting environment variables
* Copy env_example to .env and edit .env file
```bash
cp env_example .env
```


## Database
```bash
docker-compose up -d
```

## Running migrations
```bash
alembic upgrade head
```

## Running project
```bash
uvicorn backend.main:app --reload
```


