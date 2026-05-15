from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String, Text, JSON
import uuid

class BaseModel(DeclarativeBase):
    pass

class AuthToken(BaseModel):
    __tablename__ = "auth_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String,unique=True)
    description: Mapped[str] = mapped_column(String,nullable=True)

class Event(BaseModel):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    direction: Mapped[str] = mapped_column(String) #inbound / outbound
    content: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending") #pending / consumed / published

class Identity(BaseModel):
    __tablename__ = "identities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String,unique=True)
    embedding: Mapped[list[float]] = mapped_column(JSON)
