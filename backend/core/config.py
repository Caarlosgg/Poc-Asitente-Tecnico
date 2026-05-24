"""Configuración centralizada del backend usando pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    database_url: str = "postgresql+asyncpg://poc_user:poc_password@localhost:5432/poc_asistente"

    # Groq API
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_embedding_model: str = "nomic-embed-text-v1_5"

    # Parámetros del sistema
    similarity_threshold: float = 0.75
    max_vin_attempts: int = 3
    top_k_results: int = 3
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
