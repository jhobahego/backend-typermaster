from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pydantic import BaseModel
import google.generativeai as genai

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Validate required environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Get Gemini API Key
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

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

# Routes
@app.get("/texts")
async def get_random_text():
    try:
        # Updated prompt to explicitly ask for only the text
        prompt = "Generate a short English text suitable for a typing test. It should be a single paragraph, between 1 and 4 lines long. IMPORTANT: Respond ONLY with the generated text itself, without any introduction, explanation, or formatting."
        response = model.generate_content(prompt)
        # Basic error handling/check if response has text
        if response.text:
            # Clean up potential markdown or extra whitespace
            generated_text = response.text.strip()
            # Further cleaning might be needed depending on model behavior
            # Remove potential quotes if the model wraps the text
            if generated_text.startswith('"') and generated_text.endswith('"'):
                generated_text = generated_text[1:-1]
            return {"text": generated_text}
        else:
            # Fallback or raise error if generation fails
            # For now, returning a default text as fallback
            return {"text": "The quick brown fox jumps over the lazy dog."}
    except Exception as e:
        print(f"Error generating text with Gemini: {e}")
        # Fallback in case of API error
        return {"text": "Error generating text. Please try again later."}


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
