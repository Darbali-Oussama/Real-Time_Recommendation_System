from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class ItemEmbedding(Base):
    __tablename__ = 'item_embeddings'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    embedding = Column(Vector(100), nullable=False)
