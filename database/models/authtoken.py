from database.databaseManager import BaseModel
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String

class AuthToken(BaseModel):
    __tablename__ = "auth_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String,unique=True)
    description: Mapped[str] = mapped_column(String,nullable=True)
