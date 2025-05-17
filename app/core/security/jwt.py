import time

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"

# Payload follows RFC 7519
class JWTTokenPayload(BaseModel):
    iss: str
    sub: str
    exp: int
    iat: int

class JWTToken(BaseModel):
    payload: JWTTokenPayload
    access_token: str

def create_jwt_token(user_id: str) -> JWTToken:
    iat = int (time.time())
    exp = iat + get_settings().security.jwt_access_token_expire_secs

    token_payload = JWTTokenPayload(
        iss=get_settings().security.jwt_issuer,
        sub=user_id,
        exp=exp,
        iat=iat,
    )

    access_token = jwt.encode(
        token_payload.model_dump(),
        key=get_settings().security.jwt_secret_key.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )

    return JWTToken(payload=token_payload, access_token=access_token)

def verify_jwt_token(token: str) -> JWTTokenPayload:
    try:
        raw_payload = jwt.decode(
            token,
            get_settings().security.jwt_secret_key.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return JWTTokenPayload.model_validate(raw_payload)