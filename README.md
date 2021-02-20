# Basic Crud using Flask API

A simple service that runs in Python with Flask framework and using PostgreSQL. The format and approach used is to be the best knowledge of the developer for a scalable and maintainable service.

## Requirements
- [Python 3.8.5](https://www.python.org/downloads/release/python-385/)
- [Virtual environment](https://docs.python.org/3/library/venv.html)
- [PostgreSQL Database](https://www.postgresql.org/)

## How to use
- Create a virtual environment
  - `python3 -m venv venv`
- Activate the virtual environment
  - `source venv/bin/activate`
- Install all the requirements
  - `pip install -r requirements.txt`
- Create Database for the application
- Copy sample.env to .env and make necessary changes
- Initialize Database
  - `python migrate.py db init` (Applicable only for first time use or without **migrations** folder)
- Migrate database
  - `python migrate.py db migrate`
- Apply Migration
  - `python migrate.py db upgrade`
- Run the Application
  - `python run.py`
- Run the Test Cases
  - `python -m unittest discover -s tests`


## API Enpoints

The API Endpoints are published in [Postman Documenter](https://documenter.getpostman.com/view/11811884/TWDXnbbF)