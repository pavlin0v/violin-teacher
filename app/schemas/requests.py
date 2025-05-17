from pydantic import BaseModel
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
