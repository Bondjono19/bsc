from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import Type,AsyncGenerator
from sqlalchemy import select
from sqlalchemy.engine import CursorResult
from database.models import BaseModel,Identity,AuthToken,Event

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///database/data/app.db")
        self.AsyncSessionLocal = sessionmaker(self.engine,class_=AsyncSession, expire_on_commit=False)

    async def __aenter__(self) -> "DatabaseManager":
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
            #await self.insertBasic()
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
    
    async def insertBasic(self):
        tkn = AuthToken(token="token",description="test")
        await self.add(tkn)
        print("added idenntity")

databaseManager = DatabaseManager()
    