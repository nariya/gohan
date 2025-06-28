from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    preferences = Column(Text)  # JSON string for food preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    
    favorites = relationship("Favorite", back_populates="user")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    place_id = Column(String, index=True)  # Google Place ID
    place_name = Column(String)
    place_address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="favorites")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    location = Column(String)  # lat,lng format
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)