import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import task_api
from app.consumer.task_consumer import start_consumer
from app.db.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init db
    await init_db()
    # start task consumer
    asyncio.create_task(start_consumer())
    
    yield
    # close db
    await close_db()

app = FastAPI(title="Task Processing System", lifespan=lifespan)

# include routers
app.include_router(task_api.router)

# health check
@app.get("/health")
async def health():
    return {"status": "ok"}
