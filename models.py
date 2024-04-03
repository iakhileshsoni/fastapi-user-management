# Model for Registration Form

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Specify the length here
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(60), nullable=False)
