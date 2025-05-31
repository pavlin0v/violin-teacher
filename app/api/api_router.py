from fastapi import APIRouter

from app.api.endpoints import auth, users, references, sheet_music, practice_session

auth_router = APIRouter()

auth_router.include_router(auth.router, prefix="/auth", tags=["auth"])

users_router = APIRouter(
    responses={
        401: {
            "description": "No `Authorization` access token header, token is invalid or user removed",
            "content": {
                "application/json": {
                    "examples": {
                        "not authenticated": {
                            "summary": "No authorization token header",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid token": {
                            "summary": "Token validation failed, decode failed, it may be expired or malformed",
                            "value": {"detail": "Token invalid: {detailed error msg}"},
                        },
                        "removed user": {
                            "summary": "User removed",
                            "value": {"detail": "User removed"},
                        },
                    }
                }
            },
        },
    }
)

users_router.include_router(users.router, prefix="/users", tags=["users"])

references_router = APIRouter()

references_router.include_router(references.router, prefix="/references", tags=["references"])

sheet_music_router = APIRouter()

sheet_music_router.include_router(sheet_music.router, prefix="/sheet-music", tags=["sheet-music"])

practice_session_router = APIRouter()

practice_session_router.include_router(practice_session.router, prefix="/practice-sessions", tags=["practice-sessions"])