from database.databaseManager import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
import uuid

class Event(BaseModel):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    direction: Mapped[str] = mapped_column(String) #inbound / outbound
    content: Mapped[str] = mapped_column(Text)
    channel: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending") #pending / consumed / published