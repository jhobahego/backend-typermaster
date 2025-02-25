from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import random
import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel

# Load environment variables
env = os.getenv("ENV", "development")
env_file = f".env.{env}"

if not os.path.exists(env_file):
    raise RuntimeError(f"Configuration file {env_file} not found")

load_dotenv(env_file)

# Validate required environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

app = FastAPI()

# Get environment and validate allowed origins
environment = os.getenv("ENVIRONMENT", "development")
origins_env_var = "DEV_ORIGINS" if environment == "development" else "PROD_ORIGINS"
default_origins = "http://localhost:5173" if environment == "development" else ""

# Get origins based on environment
allowed_origins = os.getenv(origins_env_var, default_origins).split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

# Validate that each origin starts with http:// or https://
for origin in allowed_origins:
    if not origin.startswith(("http://", "https://")):
        raise ValueError(f"Invalid origin format: {origin}. Origins must start with http:// or https://")

print(f"Running in {environment} mode with allowed origins: {allowed_origins}")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class GameResult(Base):
    __tablename__ = "game_results"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    wpm = Column(Float)
    accuracy = Column(Float)
    real_accuracy = Column(Float)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "wpm": self.wpm,
            "accuracy": self.accuracy,
            "real_accuracy": self.real_accuracy,
            "text": self.text,
            "created_at": self.created_at.isoformat()
        }

Base.metadata.create_all(bind=engine)

# Pydantic models
class GameResultCreate(BaseModel):
    username: str
    wpm: float
    accuracy: float
    real_accuracy: float
    text: str

class GameResultResponse(BaseModel):
    id: int
    username: str
    wpm: float
    accuracy: float
    real_accuracy: float
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sample texts
TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "To be or not to be, that is the question.",
    "All that glitters is not gold.",
    "A journey of a thousand miles begins with a single step.",
    "In three words I can sum up everything I've learned about life: it goes on.",
    "Life is what happens when you're busy making other plans.",
    "The only way to do great work is to love what you do.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
]

# Routes
@app.get("/texts")
async def get_random_text():
    return {"text": random.choice(TEXTS)}

@app.post("/results", response_model=GameResultResponse)
async def save_result(result: GameResultCreate, db: Session = Depends(get_db)):
    db_result = GameResult(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@app.get("/results", response_model=dict)
async def get_results(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(GameResult).count()
    total_pages = (total + per_page - 1) // per_page
    
    query_results = db.query(GameResult)\
        .order_by(desc(GameResult.created_at))\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
    
    # Convertir los resultados a diccionarios
    results = [result.to_dict() for result in query_results]
    
    return {
        "results": results,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages
    }
