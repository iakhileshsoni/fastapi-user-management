from typing import Union

# Libraries for Registration Form
from fastapi import FastAPI, Request, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import models
from models import User

from passlib.hash import bcrypt

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

import pytz


app = FastAPI()

# Database Configuration
DATABASE_URL = "mysql://root:akhil123@localhost/fastapidb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Templates Configuration
templates = Jinja2Templates(directory="templates")


# JWT Configuration
SECRET_KEY = "7e9549775a2b3604de10e6f987b262ee4038277ac1c2ef91cebc7ed82c66237a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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



#**********************************************   JWT Token Code goes here   *********************************************#


# Create JWT Token
def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    # Define the expiration time delta (e.g., token expires in 1 hour)
    expires_delta = datetime.timedelta(hours=1)

    # Get the current time in IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
    current_time_ist = datetime.datetime.now(ist_timezone)

    # Calculate the expiration time in IST
    expires_ist = current_time_ist + expires_delta

    to_encode.update({"exp": expires_ist})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



#**********************************************   Login Form Code goes here   *********************************************#


# Login Route
@app.post("/login/")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Render Login Form
@app.get("/login/", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Render Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    db.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user_name": user.name})

# Adding this line to test