from redis.asyncio import Redis
from app.core.config import settings
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

# init redis
redis = Redis(host=settings.redis_host, decode_responses=True)

QUEUE_NAME = "task_queue"

async def enqueue_task(task_id: str):
    await redis.rpush(QUEUE_NAME, task_id)
    logger.info(f"Enqueued task {task_id}")

async def dequeue_task():
    task = await redis.blpop(QUEUE_NAME)
    if task:
        task_id = task[1]  # Redis return (queue_name, task_id)
        logger.info(f"Dequeued task {task_id}")
        return task_id
    return None
