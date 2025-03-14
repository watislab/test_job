from sqlalchemy import create_engine, Column, String, Float, ForeignKey, Identity
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class ImageDescription(Base):
    __tablename__ = 'image_descriptions'
    request_id = Column(String, primary_key=True)
    description = Column(String)
    processing_time = Column(Float)
    model_name = Column(String)
    user_id = Column(String, ForeignKey('users.id'))
    user = relationship("User", back_populates="image_descriptions")

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    username = Column(String)
    image_descriptions = relationship("ImageDescription", back_populates="user")

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)