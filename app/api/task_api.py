from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Task
from app.db.database import async_session
from app.schemas import TASK_STATUS_CANCELED, TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, TaskCreate, TaskResponse
from app.queue.redis_queue import enqueue_task
import uuid

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/task", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    task_id = str(uuid.uuid4())
    new_task = Task(id=task_id, content=task.content, status="pending")
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # add task to the queue
    await enqueue_task(task_id)

    return new_task

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

@router.patch("/task/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    # find task by id
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()

    # check if task exists and is cancelable
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.status not in [TASK_STATUS_PENDING, TASK_STATUS_PROCESSING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task cannot be canceled")

    # cancel task
    task.status = TASK_STATUS_CANCELED
    await db.commit()
    await db.refresh(task)

    return task
