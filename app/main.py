import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import task_api
from app.consumer.task_consumer import start_consumer
from app.core.config import settings
from app.db.database import init_db, close_db
from app.utils.logging import setup_logger

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting app in {settings.app_env} environment.")
    # init db
    await init_db()
    # start task consumer
    asyncio.create_task(start_consumer())
    
    yield
    # close db
    await close_db()
    logger.info("App stopped.")

app = FastAPI(title="Task Processing System", lifespan=lifespan)

# include routers
app.include_router(task_api.router)

# health check
@app.get("/health")
async def health():
    return {"status": "ok"}
