from redis.asyncio import Redis
from app.core.config import settings
from app.utils.logging import setup_logger
from app.utils.metrics import metrics_queue_length, metrics_queue_push_count, metrics_queue_push_fail_count, metrics_queue_pop_count, metrics_queue_pop_fail_count

logger = setup_logger(__name__)

# init redis
redis = Redis(host=settings.redis_host, decode_responses=True)

QUEUE_NAME = "task_queue"

async def enqueue_task(task_id: str):
    metrics_queue_push_count.inc()

    try:
        await redis.rpush(QUEUE_NAME, task_id)
    except Exception as e:
        metrics_queue_push_fail_count.inc()
        e = Exception(f"Failed to push task {task_id} to redis queue: {e}")
        logger.error(e)
        raise e
    
    metrics_queue_length.inc()
    logger.info(f"Enqueued task {task_id}")

async def dequeue_task():
    try:
        task = await redis.blpop(QUEUE_NAME)
    except Exception as e:
        metrics_queue_pop_fail_count.inc()
        e = Exception(f"Failed to pop task from redis queue: {e}")
        logger.error(e)
        raise e

    if task:
        metrics_queue_pop_count.inc()
        task_id = task[1]  # Redis return (queue_name, task_id)
        metrics_queue_length.dec()
        logger.info(f"Dequeued task {task_id}")
        return task_id
    return None
