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

