from sqlalchemy import Column, Integer, String, Text
from .database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    review = Column(Text)
    ai_response = Column(Text)
    ai_summary = Column(Text)
    ai_action = Column(Text)
