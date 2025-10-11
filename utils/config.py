
# This file manages application configuration using Pydantic's BaseSettings.
# It allows loading settings from environment variables, which is a best practice
# for separating configuration from code.

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings. Values are loaded from environment variables.
    A .env file can be used for local development.
    """
    # API Keys
    GEMINI_API_KEY: str = "YOUR_GEMINI_API_KEY_HERE"

    # Model Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Orchestrator Logic
    ROUTER_TOP_K: int = 3 # Number of candidate tools to select

    # General
    LOG_LEVEL: str = "INFO"

    class Config:
        # This allows loading variables from a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single instance of the settings to be imported by other modules
settings = Settings()

# It's good practice to check for essential keys at startup
if settings.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("WARNING: GEMINI_API_KEY is not set. Please set it in your environment or a .env file.")
