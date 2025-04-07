from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from config.database import engine, Base
from routers import texts, results

# Create database tables if they don't exist
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created successfully.")
except Exception as e:
    print(f"Error creating database tables: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="TyperMaster API",
    description="API for the TyperMaster typing game.",
    version="1.0.0"
)

# Enable CORS using settings from config.py
if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    print("Warning: No allowed origins configured for CORS.")


# Include routers
app.include_router(texts.router)
app.include_router(results.router)

# Root endpoint for health check or basic info
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the TyperMaster API!"}

