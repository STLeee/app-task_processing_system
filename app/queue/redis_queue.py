import os
from redis.asyncio import Redis

# init redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis = Redis(host=REDIS_HOST, decode_responses=True)

QUEUE_NAME = "task_queue"

async def enqueue_task(task_id: str):
    await redis.rpush(QUEUE_NAME, task_id)
    print(f"Enqueued task {task_id}")

async def dequeue_task():
    task = await redis.blpop(QUEUE_NAME)
    if task:
        task_id = task[1]  # Redis return (queue_name, task_id)
        print(f"Dequeued task {task_id}")
        return task_id
    return None
