from pydantic import BaseModel, ConfigDict
from app.models.enums import UserRole, SessionStatus
from datetime import datetime

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

class PracticeSessionCreateRequest(BaseRequest):
    sheet_id: str
    midi_file_id: str
    metric_pref: dict | None = None

    model_config = ConfigDict(from_attributes=True)

class PracticeSessionUpdateRequest(BaseRequest):
    status: SessionStatus | None = None
    metric_pref: dict | None = None
    audio_url: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
