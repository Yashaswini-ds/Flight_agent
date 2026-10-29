import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FlightAgent Production Booking Engine"
    ENV: str = "development"
    PORT: int = 8000
    
    # PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/flight_agent_db"
    TEST_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/flight_agent_test_db"
    
    # Auth
    JWT_SECRET: str = "super-secret-production-quality-jwt-signing-key-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Financial Demo Rules
    DEMO_TAX_PERCENTAGE: float = 18.0
    
    # LLM Settings
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-3.5-turbo"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
