from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
import mysql.connector
from starlette.responses import RedirectResponse

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="todo_db"
)
cursor = db.cursor()

# FastAPI Instance
app = FastAPI()

# Security
security = HTTPBasic()


# Models
class Todo(BaseModel):
    """
    Represents a Todo item with a title and description.
    """
    title: str
    description: str


class User(BaseModel):
    """
    Represents a User with a username and password.
    """
    username: str
    password: str


# Authentication
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticates the user using basic HTTP authentication.
    """
    if credentials.username != "user" or credentials.password != "password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


# CRUD Operations
@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, authenticated: bool = Depends(authenticate_user)):
    """
    Creates a new todo item.
    """
    query = "INSERT INTO todos (title, description) VALUES (%s, %s)"
    values = (todo.title, todo.description)
    cursor.execute(query, values)
    db.commit()
    return todo


@app.get("/todos/", response_model=List[Todo])
def read_todos(authenticated: bool = Depends(authenticate_user)):
    """
    Retrieves all todo items.
    """
    query = "SELECT title, description FROM todos"
    cursor.execute(query)
    result = cursor.fetchall()
    todos = [{"title": title, "description": description} for title, description in result]
    return todos


@app.put("/todos/{todo_id}/", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, authenticated: bool = Depends(authenticate_user)):
    """
    Updates an existing todo item.
    """
    query = "UPDATE todos SET title = %s, description = %s WHERE id = %s"
    values = (todo.title, todo.description, todo_id)
    cursor.execute(query, values)
    db.commit()
    return todo


@app.delete("/todos/{todo_id}/", response_model=Todo)
def delete_todo(todo_id: int, authenticated: bool = Depends(authenticate_user)):
    """
    Deletes an existing todo item.
    """
    query = "DELETE FROM todos WHERE id = %s"
    values = (todo_id,)
    cursor.execute(query, values)
    db.commit()
    return {"message": "Todo deleted successfully"}


# Documentation
@app.get("/")
async def root():
    """
    Welcome message.
    """
    return {"message": "Welcome to the Todo List API"}


@app.get("/docs")
async def get_documentation():
    """
    Redirects to the API documentation.
    """
    return RedirectResponse(url="/docs")
