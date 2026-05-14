from database.databaseManager import BaseModel
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String, Text

class Identity(BaseModel):
    __tablename__ = "identities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String,unique=True)
    embedding: Mapped[str] = mapped_column(Text)
