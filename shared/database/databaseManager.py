from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import Type,AsyncGenerator
from sqlalchemy import select, text
from sqlalchemy.engine import CursorResult
from shared.database.models import BaseModel,Identity,AuthToken,Event
import os

class DatabaseManager:
    def __init__(self):
        self.DB_USER = os.getenv("POSTGRES_USER")
        self.DB_HOST = os.getenv("POSTGRES_HOST")
        self.DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        self.DB_PORT = os.getenv("POSTGRES_PORT")
        self.DB = os.getenv("POSTGRES_DB")
        self.engine = create_async_engine(f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB}")
        self.AsyncSessionLocal = sessionmaker(self.engine,class_=AsyncSession, expire_on_commit=False)

    async def __aenter__(self) -> "DatabaseManager":
        async with self.engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(BaseModel.metadata.create_all)
            await self.insertBasic()
            return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.engine.dispose()
    
    async def get_database(self) -> AsyncGenerator[AsyncSession,None]:
        async with self.AsyncSessionLocal() as session:
            yield session

    async def execute(self,query) -> list:
        async with self.AsyncSessionLocal() as db:
            result = await db.execute(query)
            return result.scalars().all()
        
    async def add(self,object: BaseModel) -> BaseModel:
        async with self.AsyncSessionLocal() as db:
            db.add(object)
            await db.commit()
            await db.refresh(object)
            return object
        
    async def remove(self,id: int, model : Type[BaseModel]) -> bool:
        async with self.AsyncSessionLocal() as db:
            res = await db.execute(select(model).where(model.id == id))
            object = res.scalar_one_or_none()
            if not object:
                return False
            await db.delete(object)
            await db.commit()
            return True
    
    async def update(self, object: BaseModel) -> None:
        async with self.AsyncSessionLocal() as db:
            await db.merge(object)
            await db.commit()
    
    async def fetchAll(self, model: BaseModel) -> None:
        async with self.AsyncSessionLocal() as db:
            res = await db.execute(select(model))
            return res.scalars().all()

    async def insertBasic(self):
        async with self.AsyncSessionLocal() as db:
            res = await db.execute(select(AuthToken).where(AuthToken.description == "test"))
            if not res.scalar_one_or_none() == None:
                return
        tkn = AuthToken(token="token",description="test")
        await self.add(tkn)
        print("added idenntity")

databaseManager = DatabaseManager()