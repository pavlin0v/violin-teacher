from fastapi import FastAPI

from app.api.api_router import auth_router, users_router, references_router, sheet_music_router, practice_session_router

app = FastAPI(
    title="violin-teacher",
    version="0.1.0",
    description="Чудесный сервис для оценки и обучения игре на скрипке",
    openapi_url="/openapi.json",
    docs_url="/",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(references_router)
app.include_router(sheet_music_router)
app.include_router(practice_session_router)