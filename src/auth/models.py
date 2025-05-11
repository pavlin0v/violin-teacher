from src.models import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
        index=True,
        doc="Username for authentication."
    )
    password: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Hashed password."
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, created_at={self.created_at})>"
    # username = Column(
    #     "username",
    #     STRING,
    #     nullable=False,
    #     unique=True,
    #     index=True,
    #     doc="Username for authentication."
    # )
    # password = Column(
    #     "password",
    #     STRING,
    #     nullable=False,
    #     index=True,
    #     doc="Hashed password."
    # )