from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str
    deepseek_model: str = "deepseek-chat"
    max_log_chars: int = 8000

    model_config = {"env_file": ".env"}


settings = Settings()
