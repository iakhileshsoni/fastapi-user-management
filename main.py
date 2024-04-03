from typing import Union

# Libraries for Registration Form
from fastapi import FastAPI, Request, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import models
from models import User

from passlib.hash import bcrypt

# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext


app = FastAPI()

# Database Configuration
DATABASE_URL = "mysql://root:akhil123@localhost/fastapidb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Templates Configuration
templates = Jinja2Templates(directory="templates")


# # Password Hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# # OAuth2 Scheme for Authentication
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#**********************************************   Registration Form Code goes here   *********************************************#


# Register route
@app.post("/register/")
async def register(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    hashed_password = bcrypt.hash(password)
    user = User(name=name, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/users", status_code=303)

# Render Registration Form
@app.get("/register/", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Render Registration Form and User Table
@app.get("/users/", response_class=HTMLResponse)
async def show_registration_form_and_users(request: Request):
    # Fetch all registered users
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})



#**********************************************   Login Form Code goes here   *********************************************#


# Login Route
@app.post("/login/")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return RedirectResponse(url="/dashboard", status_code=303)

# Render Login Form
@app.get("/login/", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Render Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request, db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


















#*************************************************   To-do App Code goes here   *************************************************#


# Libraries to work with To-do App

# from fastapi import HTTPException, Form
# from pydantic import BaseModel
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles

# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker


# MySQL Database Configuration
# DATABASE_URL = "mysql://root:akhil123@localhost/fastapidb"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create FastAPI app
# app = FastAPI()

# # Mount the static files directory
# app.mount("/static", StaticFiles(directory="templates"), name="static")

# # SQLAlchemy models
# Base = declarative_base()

# class Todo(Base):
#     __tablename__ = "todos"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)

# # Pydantic models
# class TodoCreate(BaseModel):
#     title: str
#     description: str

# class TodoUpdate(BaseModel):
#     title: str
#     description: str

# class TodoResponse(BaseModel):
#     id: int
#     title: str
#     description: str

# # Routes
# @app.post("/todos/", response_model=TodoResponse)
# def create_todo(todo: TodoCreate):
#     db = SessionLocal()
#     db_todo = Todo(**todo.dict())
#     db.add(db_todo)
#     db.commit()
#     db.refresh(db_todo)
#     db.close()
#     return db_todo

# @app.get("/todos/{todo_id}", response_model=TodoResponse)
# def read_todo(todo_id: int):
#     db = SessionLocal()
#     todo = db.query(Todo).filter(Todo.id == todo_id).first()
#     db.close()
#     if todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     return todo

# @app.put("/todos/{todo_id}", response_model=TodoResponse)
# def update_todo(todo_id: int, todo: TodoUpdate):
#     db = SessionLocal()
#     db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     for attr, value in todo.dict().items():
#         setattr(db_todo, attr, value)
#     db.commit()
#     db.refresh(db_todo)
#     db.close()
#     return db_todo

# @app.delete("/todos/{todo_id}")
# def delete_todo(todo_id: int):
#     db = SessionLocal()
#     db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
#     if db_todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     db.delete(db_todo)
#     db.commit()
#     db.close()
#     return {"message": "Todo deleted successfully"}

# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     # Return the HTML form
#     return open("templates/index.html", "r").read()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)