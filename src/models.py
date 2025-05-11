import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, CHAR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[CHAR] = mapped_column(CHAR(32), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())