"""
Configuration settings for AI Code Reviewer.

This module contains all configuration settings for the application,
including environment variables, API keys, and system parameters.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name (str): Name of the application.
        debug (bool): Debug mode flag.
        api_host (str): API server host.
        api_port (int): API server port.
        llm_provider (str): LLM provider (local/openai/gemini/anthropic).
        openai_api_key (Optional[str]): OpenAI API key if using OpenAI.
        vector_db_url (str): Vector database connection URL.
        postgres_url (Optional[str]): PostgreSQL connection URL for metadata.
    """
    
    # Application settings
    app_name: str = "AI Code Reviewer"
    debug: bool = False
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    
    # LLM settings
    llm_provider: str = "local"  # local, openai, gemini, anthropic
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Local LLM settings
    local_llm_model_path: Optional[str] = None
    local_llm_device: str = "auto"  # auto, cpu, cuda
    
    # Database settings
    vector_db_url: str = "sqlite:///./vector_db.sqlite"
    postgres_url: Optional[str] = None
    
    # Analysis settings
    max_file_size_mb: int = 10
    supported_languages: list = ["python", "java", "kotlin"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 