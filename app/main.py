from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init db
    await init_db()
    yield
    # close db
    await close_db()

app = FastAPI(title="Task Processing System", lifespan=lifespan)

# health check
@app.get("/health")
async def health():
    return {"status": "ok"}
