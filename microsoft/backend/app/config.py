from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/venturescope"
    
    # Hindsight by Vectorize
    hindsight_api_token: Optional[str] = None  # hsk_... bearer token
    hindsight_api_key: Optional[str] = None    # Alias for api_token
    hindsight_api_url: str = "https://api.hindsight.vectorize.io"
    hindsight_bank_id: str = "venturescope-market-intelligence"
    hindsight_mode: str = "cloud"              # "cloud" (default) or "mock"
    
    # LLM
    groq_api_key: Optional[str] = None
    
    # Maps / External Evidence
    mapbox_token: Optional[str] = None
    google_maps_api_key: Optional[str] = None
    
    # Auth
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # App
    app_env: str = "development"
    debug: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def sync_hindsight_credentials(self):
        # Allow either HINDSIGHT_API_TOKEN or HINDSIGHT_API_KEY
        if not self.hindsight_api_token and self.hindsight_api_key:
            self.hindsight_api_token = self.hindsight_api_key
        elif not self.hindsight_api_key and self.hindsight_api_token:
            self.hindsight_api_key = self.hindsight_api_token
        return self

settings = Settings()
