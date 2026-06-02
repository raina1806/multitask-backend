from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")

class TodoCreate(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()

class TodoUpdate(BaseModel):
    text: str | None = None
    completed: bool | None = None


class NoteCreate(BaseModel):
    title: str
    body: str

    @field_validator("title", "body")
    @classmethod
    def fields_must_not_be_empty(cls, v):
        return v.strip()

class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None

@app.get("/")
def root():
    return {"message": "Todo API is running"}

@app.get("/api/todos")
def get_todos():
    try:
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        todos = cursor.fetchall()
        return todos
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/todos")
def create_todo(todo: TodoCreate):
    try:
        cursor.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING *",
            (todo.text,)
        )
        new_todo = cursor.fetchone()
        conn.commit()
        return new_todo
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/todos/{id}")
def update_todo(id: int, todo: TodoUpdate):
    try:
        cursor.execute("SELECT * FROM todos WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")

        new_text = todo.text if todo.text is not None else existing["text"]
        new_completed = todo.completed if todo.completed is not None else existing["completed"]

        cursor.execute(
            "UPDATE todos SET text = %s, completed = %s WHERE id = %s RETURNING *",
            (new_text, new_completed, id)
        )
        updated_todo = cursor.fetchone()
        conn.commit()
        return updated_todo
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/todos/{id}")
def delete_todo(id: int):
    try:
        cursor.execute("SELECT * FROM todos WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")

        cursor.execute("DELETE FROM todos WHERE id = %s", (id,))
        conn.commit()
        return {"message": "Todo deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/notes")
def get_notes():
    try:
        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        notes = cursor.fetchall()
        return notes
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/notes")
def create_note(note: NoteCreate):
    try:
        cursor.execute(
            "INSERT INTO notes (title, body) VALUES (%s, %s) RETURNING *",
            (note.title, note.body)
        )
        new_note = cursor.fetchone()
        conn.commit()
        return new_note
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/notes/{id}")
def update_note(id: int, note: NoteUpdate):
    try:
        cursor.execute("SELECT * FROM notes WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Note not found")

        new_title = note.title if note.title is not None else existing["title"]
        new_body = note.body if note.body is not None else existing["body"]

        cursor.execute(
            "UPDATE notes SET title = %s, body = %s WHERE id = %s RETURNING *",
            (new_title, new_body, id)
        )
        updated_note = cursor.fetchone()
        conn.commit()
        return updated_note
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/notes/{id}")
def delete_note(id: int):
    try:
        cursor.execute("SELECT * FROM notes WHERE id = %s", (id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Note not found")

        cursor.execute("DELETE FROM notes WHERE id = %s", (id,))
        conn.commit()
        return {"message": "Note deleted"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))