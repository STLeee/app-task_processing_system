import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Task
from app.db.database import async_session
from app.queue.redis_queue import dequeue_task

async def process_task(task_id: str, db: AsyncSession):
    # fetch task
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()

    # check task status
    if not task:
        print(f"Task {task_id} not found.")
        return
    if task.status != "pending":
        print(f"Task {task_id} already processed or canceled.")
        return
    
    # process task
    task.status = "processing"
    await db.commit()
    await asyncio.sleep(3)
    task.status = "completed"
    await db.commit()
    print(f"Task {task_id} completed.")

async def start_consumer():
    while True:
        try:
            task_id = await dequeue_task()
        except Exception as e:
            print(f"get task error: {e}")
        else:
            if task_id:
                try:
                    async with async_session() as db:
                        await process_task(task_id, db)
                except Exception as e:
                    print(f"process task error: {e}")
            else:
                await asyncio.sleep(1)
