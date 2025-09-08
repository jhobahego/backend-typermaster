import os
from typing import List

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEV_ORIGINS = os.getenv("DEV_ORIGINS", "http://localhost:5173")
PROD_ORIGINS = os.getenv("PROD_ORIGINS", "")
ENVIRONMENT = os.getenv("ENVIRONMENT")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
if not ENVIRONMENT:
    raise ValueError("ENVIRONMENT is not set in the environment variables.")
if ENVIRONMENT not in ["development", "production"]:
    raise ValueError("ENVIRONMENT must be either 'development' or 'production'.")
if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL is not set in the environment variables.")


class Settings(BaseSettings):
    database_url: str = Field(default="", validation_alias="DATABASE_URL")
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    environment: str = Field("development", validation_alias="ENVIRONMENT")
    dev_origins_str: str = Field("http://localhost:5173", validation_alias="DEV_ORIGINS")
    prod_origins_str: str = Field("", validation_alias="PROD_ORIGINS")
    gemini_model: str = Field("gemini-2.0-flash-lite-001", validation_alias="GEMINI_MODEL")

    # Configure BaseSettings to look for a .env file
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore' # Ignore extra fields from env/dotenv
    )

    @property
    def allowed_origins(self) -> List[str]:
        """Compute allowed origins based on environment"""
        origins_str = self.dev_origins_str if self.environment == 'development' else self.prod_origins_str

        if not origins_str:
            return []

        origins_list = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

        # Validate format for each origin
        validated_origins = []
        for origin in origins_list:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(f"Invalid origin format: {origin}. Origins must start with http:// or https://")
            try:
                AnyHttpUrl(origin) # Further validation
                validated_origins.append(origin)
            except ValueError:
                raise ValueError(f"Invalid URL format for origin: {origin}")
        return validated_origins
    

settings = Settings(
    database_url=DATABASE_URL, 
    gemini_api_key=GEMINI_API_KEY,
    gemini_model=GEMINI_MODEL, 
    environment=ENVIRONMENT, 
    dev_origins_str=DEV_ORIGINS, 
    prod_origins_str=PROD_ORIGINS
)

