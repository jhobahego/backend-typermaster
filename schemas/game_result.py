from pydantic import BaseModel
from datetime import datetime
from typing import List

# Schema for creating a new game result (request body)
class GameResultCreate(BaseModel):
    username: str
    wpm: float
    accuracy: float
    real_accuracy: float
    text: str

# Schema for returning a game result (response body)
class GameResultResponse(BaseModel):
    id: int
    username: str
    wpm: float
    accuracy: float
    real_accuracy: float
    text: str
    created_at: datetime | None # Allow None if conversion fails or not set

    class Config:
        from_attributes = True # Enable ORM mode
        json_encoders = {
            # Custom encoder for datetime to ensure ISO format
            datetime: lambda v: v.isoformat() if v else None
        }

# Schema for the paginated response
class PaginatedGameResults(BaseModel):
    results: List[GameResultResponse]
    page: int
    per_page: int
    total: int
    total_pages: int
