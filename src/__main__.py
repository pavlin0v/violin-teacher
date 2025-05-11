from fastapi import FastAPI
from uvicorn import run

from config import get_settings


app = FastAPI()

@app.get("/ping/")
async def ping():
    return {"ping": "pong"}

if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "__main__:app",
        host=settings_for_application.APP_ADDRESS,
        port=settings_for_application.APP_PORT,
    )
