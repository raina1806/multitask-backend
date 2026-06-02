# Multitask API

FastAPI backend for the Multitask productivity app.

## Endpoints
- GET/POST/PUT/DELETE /api/todos
- GET/POST/PUT/DELETE /api/notes

## Tech Stack
- FastAPI
- PostgreSQL
- psycopg2
- Pydantic

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Create `.env` with database credentials
6. Run: `uvicorn main:app --reload`