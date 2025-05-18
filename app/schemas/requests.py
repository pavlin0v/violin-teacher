from pydantic import BaseModel, ConfigDict
from app.models.enums import UserRole

class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass

class RefreshTokenRequest(BaseRequest):
    refresh_token: str

class UserCreateRequest(BaseRequest):
    login: str
    password: str

class UserUpdatePasswordRequest(BaseRequest):
    password: str

class SheetMusicRequest(BaseRequest):
    title:       str | None = None
    composer:    str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
