from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models.schemas.auth_schemas import Role
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'


    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), unique=False, nullable=False)
    role = Column(Enum(Role), default=Role.USER)
    