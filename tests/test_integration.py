# tests/test_integration.py

import asyncio
import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models import Task, async_session
from app.consumer import task_consumer

@pytest.mark.asyncio
async def test_full_task_flow():
    # 
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_response = await ac.post("/task", json={"content": "test_content"})
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # check task status
    async with async_session() as db:
        task = await Task.get(task_id, db)
    assert task.status == "pending"

    # start task consumer
    task_consumer.start_consumer()
    await asyncio.sleep(1)

    # check task status
    async with async_session() as db:
        task = await Task.get(task_id, db)
    assert task.status == "processing"

    # wait for task processing
    await asyncio.sleep(3)

    # check task status
    async with async_session() as db:
        task = await Task.get(task_id, db)
    assert task.status == "completed"
