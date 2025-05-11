from datetime import datetime
from pydantic import BaseModel, Field

class RegistrationSchema(BaseModel):
    username: str = Field(min_length=1, max_length=128, pattern="^[A-Za-z0-9-_]+$")
    password: str = Field(min_length=8, max_length=128)

class UserSchema(RegistrationSchema):
    created_at: datetime
    updated_at: datetime
