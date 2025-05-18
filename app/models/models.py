import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    BOOLEAN,
    Enum,
    ForeignKey,
    Index,
    JSON,
    Numeric,
    String,
    func,
    text,
    BigInteger,
    DateTime,
    Boolean,
    SmallInteger,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from app.models.enums import UserRole, SessionStatus, FileStatus



class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(256))
    login: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    materials: Mapped[List["Material"]] = relationship(back_populates="user")
    sheets: Mapped[List["SheetMusic"]] = relationship(back_populates="owner")
    midi_files: Mapped[List["MidiFile"]] = relationship(back_populates="uploader")
    sessions: Mapped[List["PracticeSession"]] = relationship(back_populates="user")
    reports: Mapped[List["Report"]] = relationship(back_populates="user")
    user_metric_pref: Mapped["UserMetricPref"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

class UserMetricPref(Base):
    __tablename__ = "user_metric_pref"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    metric_pref: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )

    user: Mapped["User"] = relationship(back_populates="user_metric_pref")

class Material(Base):
    """Учебные материалы (markdown + вложения)."""
    __tablename__ = "materials"

    material_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    author_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )
    content_md: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship(back_populates="materials")

class SheetMusic(Base):
    """Произведение: заголовок, композитор, описание."""
    __tablename__ = "sheet_music"

    sheet_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    composer: Mapped[str | None] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(String)

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    owner: Mapped["User"] = relationship(back_populates="sheets")

    midi_files: Mapped[list["MidiFile"]] = relationship(
        back_populates="sheet", cascade="all, delete-orphan"
    )

    sessions: Mapped[list["PracticeSession"]] = relationship(back_populates="sheet")


class MidiFile(Base):
    """MIDI-варианты для произведения."""
    __tablename__ = "midi_files"

    midi_file_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    sheet_id: Mapped[str] = mapped_column(
        ForeignKey("sheet_music.sheet_id", ondelete="CASCADE"),
        nullable=False
    )
    uploaded_by: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus),
        nullable=False,
        default=FileStatus.PENDING
    )
    version: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0")
    )
    parsed_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )

    sheet: Mapped["SheetMusic"] = relationship(back_populates="midi_files")
    uploader: Mapped["User"] = relationship(back_populates="midi_files")
    sessions: Mapped[list["PracticeSession"]] = relationship(
        back_populates="midi_file"
    )


class PracticeSession(Base):
    """Факт запуска и прохождения произведения пользователем."""
    __tablename__ = "practice_sessions"

    session_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )
    sheet_id: Mapped[str] = mapped_column(
        ForeignKey("sheet_music.sheet_id", ondelete="RESTRICT"),
        nullable=False
    )
    midi_file_id: Mapped[str] = mapped_column(
        ForeignKey("midi_files.midi_file_id", ondelete="RESTRICT"),
        nullable=False
    )

    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus),
        nullable=False,
        default=SessionStatus.DRAFT
    )

    metric_pref: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )
    audio_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True
    )

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="sessions")
    sheet: Mapped["SheetMusic"] = relationship(back_populates="sessions")
    midi_file: Mapped["MidiFile"] = relationship(back_populates="sessions")
    live_metrics: Mapped[list["LiveSessionMetric"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    report: Mapped["Report"] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_session_user_status", "user_id", "status"),
    )

class LiveSessionMetric(Base):
    """Метрики, получаемые в реальном времени."""
    __tablename__ = "live_session_metrics"

    live_metric_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )
    offset_ms: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    matric_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )
    value: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    window_ms: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    algo_version: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0")
    )


    session: Mapped["PracticeSession"] = relationship(back_populates="live_metrics")

class Report(Base):
    """Финальный отчёт после завершения сессии."""
    __tablename__ = "reports"

    report_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda _: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("practice_sessions.session_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )
    overall_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False
    )
    summary: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb")
    )
    algo_version: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        server_default=text("0")
    )

    session: Mapped["PracticeSession"] = relationship(back_populates="report")
    user: Mapped["User"] = relationship(back_populates="reports")

    __table_args__ = (
        Index("idx_report_user_session", "user_id", "session_id", "created_at"),
    )