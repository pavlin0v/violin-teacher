import enum

class UserRole(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"

class SessionStatus(enum.StrEnum):
    DRAFT = "draft"
    PLAYING = "playing"
    DONE = "done"
    ERROR = "error"

class FileStatus(enum.StrEnum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    READY = "ready"
    ERROR = "error"
    PENDING = "pending"