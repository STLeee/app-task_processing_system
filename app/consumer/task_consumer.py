import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Task
from app.db.database import async_session
from app.queue.redis_queue import dequeue_task
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

async def process_task(task_id: str, db: AsyncSession):
    # fetch task
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()

    # check task status
    if not task:
        logger.warning(f"Task {task_id} not found.")
        return
    if task.status != "pending":
        logger.warning(f"Task {task_id} already processed or canceled.")
        return
    
    # process task
    try:
        task.status = "processing"
        await db.commit()
        await asyncio.sleep(3)
        task.status = "completed"
        await db.commit()
        logger.info(f"Task {task_id} completed.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Task {task_id} processing error: {e}")

async def start_consumer():
    while True:
        try:
            task_id = await dequeue_task()
        except Exception as e:
            logger.error(f"get task error: {e}")
        else:
            if task_id:
                async with async_session() as db:
                    await process_task(task_id, db)
            else:
                await asyncio.sleep(1)
