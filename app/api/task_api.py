from fastapi import APIRouter, HTTPException, status, Depends
from prometheus_client import Counter, Gauge
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Task
from app.db.models import async_session
from app.schemas import TASK_STATUS_CANCELED, TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, TaskCreate, TaskResponse
from app.queue.redis_queue import enqueue_task
from app.utils.logging import setup_logger
from app.utils.metrics import (
    metrics_task_status,
    metrics_task_create_request_count,
    metrics_task_create_success_count,
    metrics_task_create_fail_count,
    metrics_task_get_request_count,
    metrics_task_cancel_request_count,
    metrics_task_cancel_success_count,
    metrics_task_cancel_fail_count
)

logger = setup_logger(__name__)

router = APIRouter()

async def get_db():
    async with async_session() as db:
        yield db

@router.post("/task", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    metrics_task_create_request_count.inc()

    new_task = Task(task.content)

    # save task to the database
    try:
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
    except Exception as e:
        await db.rollback()

        metrics_task_create_fail_count.inc()
        logger.error(f"Task creation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task creation error")

    # add task to the queue
    try:
        await enqueue_task(new_task.id)
    except Exception as e:
        # rollback task creation if enqueue fails
        db.delete(new_task)
        await db.commit()

        metrics_task_create_fail_count.inc()
        logger.error(f"Task creation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task creation error")

    metrics_task_status.labels(new_task.status).inc()
    metrics_task_create_success_count.inc()
    logger.info(f"Task created with ID: {new_task.id}")
    return new_task

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    metrics_task_get_request_count.inc()

    # find task by id
    task = await Task.get(task_id, db)

    if not task:
        logger.error(f"Task {task_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

@router.patch("/task/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str, db: AsyncSession = Depends(get_db)):
    metrics_task_cancel_request_count.inc()

    # find task by id
    task = await Task.get(task_id, db)

    # check if task exists and is cancelable
    if not task:
        logger.error(f"Task {task_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.status not in [TASK_STATUS_PENDING, TASK_STATUS_PROCESSING]:
        logger.warning(f"Task {task_id} cannot be canceled as it is already {task.status}.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task cannot be canceled")

    # cancel task
    try:
        task.status = TASK_STATUS_CANCELED
        await db.commit()
        await db.refresh(task)
    except Exception as e:
        await db.rollback()

        metrics_task_cancel_fail_count.inc()
        logger.error(f"Task {task_id} cancel error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Task cancel error")

    metrics_task_status.labels(task.status).inc()
    metrics_task_cancel_success_count.inc()
    logger.info(f"Task {task_id} canceled.")
    return task
