from sqlalchemy import create_engine

from src.auth.models import Base

engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)