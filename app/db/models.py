import uuid
from fastapi import Depends
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import settings
from app.schemas import TASK_STATUS_PENDING

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
    status = Column(String, nullable=False, default=TASK_STATUS_PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __init__(self, content: str, status: str=TASK_STATUS_PENDING):
        self.id = str(uuid.uuid4())
        self.content = content
        self.status = status

    def __repr__(self):
        return f"<Task {self.id}>"
    
    @classmethod
    async def get(cls, task_id: str, db: AsyncSession) -> "Task":
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        return task
