from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.models.enums import SessionStatus


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int

class UserResponse(BaseResponse):
    user_id: str
    login: str

class SheetMusicResponse(BaseResponse):
    sheet_id: str
    title: str
    author_name: str
    uploaded_by: str
    uploaded_at: datetime

class PracticeSessionResponse(BaseResponse):
    session_id: str
    user_id: str
    sheet_id: str
    midi_file_id: str
    status: SessionStatus
    metric_pref: dict
    audio_url: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    created_at: datetime
    updated_at: datetime