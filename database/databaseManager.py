from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import Type,AsyncGenerator
from sqlalchemy import select
from sqlalchemy.engine import CursorResult


class BaseModel(DeclarativeBase):
    pass

class DatabaseManager:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///database/data/app.db")
        self.AsyncSessionLocal = sessionmaker(self.engine,class_=AsyncSession, expire_on_commit=False)

    async def initializeDatabase(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
    
    async def get_database(self) -> AsyncGenerator[AsyncSession,None]:
        async with self.AsyncSessionLocal() as session:
            yield session

    async def execute(self,query) -> CursorResult:
        async with self.AsyncSessionLocal() as db:
            result = await db.execute(query)
            return result
        
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
    

databaseManager = DatabaseManager()
    