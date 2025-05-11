from os import environ

from pydantic_settings import BaseSettings

class DefaultSettings(BaseSettings):

    APP_ADDRESS: str = environ.get("APP_ADDRESS", "127.0.0.1")
    APP_PORT: int = int(environ.get("APP_PORT", 8000))

def get_settings():
    return DefaultSettings()