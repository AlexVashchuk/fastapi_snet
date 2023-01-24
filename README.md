# Quick start

### Preparing
Install and run your sql database service. Below instructions are for postgresql.
The code is written on python v.3.10

### Creating virtual environment is recommended. Run following:
1. python3 -r venv venv
2. source /venv/bin/activate

### Install all the modules nessecary and init migrations
3. pip install requirements.txt
4. alembic init migrations

## IMPORTANT
## In alembic.ini comment the variable sqlalchemy.url
## Apply you login@password and db name in db.py

### To create migrations and migrate run:
5. alembic revision --autogenerate -m "Your comment"
6. alembic upgrade head

### Run the application:
7. uvicorn main:app


