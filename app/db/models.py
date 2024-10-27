import uuid
from fastapi import Depends
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings

# async engine and session
engine = create_async_engine(settings.database_url, echo=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class Task(Base):
    __tablename__ = "task"

    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Task {self.id}>"

    @classmethod
    async def create(cls, content: str, db: AsyncSession) -> "Task":
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, content=content, status="pending")
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @classmethod
    async def get(cls, task_id: str, db: AsyncSession) -> "Task":
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        return task
