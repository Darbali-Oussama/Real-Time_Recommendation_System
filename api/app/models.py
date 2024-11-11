from sqlalchemy import Column, Integer, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

Base = declarative_base()

class ItemEmbedding(Base):
    __tablename__ = 'item_embeddings'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    embedding = Column(Vector(100), nullable=False)

    class Config:
        orm_mode = True

class UserRating(Base):
    __tablename__ = 'user_rating'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    book = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    timeQuestion = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id: int, book: str, rating: float):
        self.user_id = user_id
        self.book = book
        self.rating = rating
        self.timeQuestion = datetime.utcnow()