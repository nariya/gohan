from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    preferences: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    email: str
    preferences: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteCreate(BaseModel):
    user_id: int
    place_id: str
    place_name: str
    place_address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    notes: Optional[str] = None

class Favorite(BaseModel):
    id: int
    user_id: int
    place_id: str
    place_name: str
    place_address: str
    latitude: float
    longitude: float
    rating: Optional[float]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchHistoryCreate(BaseModel):
    query: str
    location: str
    results_count: int

class SearchHistory(BaseModel):
    id: int
    query: str
    location: str
    results_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlaceSearchResponse(BaseModel):
    results: List[Any]
    status: str