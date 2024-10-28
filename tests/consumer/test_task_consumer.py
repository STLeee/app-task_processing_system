import pytest
from unittest import mock
import pytest_asyncio
from app.consumer.task_consumer import process_task
from app.db.models import Task

@pytest_asyncio.fixture
def mock_task():
    with mock.patch('app.consumer.task_consumer.Task') as MockTask:
        yield MockTask

@pytest_asyncio.fixture
def mock_db():
    with mock.patch('app.consumer.task_consumer.async_session') as MockSession:
        yield MockSession

@pytest_asyncio.fixture
def mock_logger():
    with mock.patch('app.consumer.task_consumer.logger') as MockLogger:
        yield MockLogger

@pytest.mark.asyncio
async def test_process_task_not_found(mock_task, mock_db, mock_logger):
    mock_task.get = mock.AsyncMock(return_value=None)
    db = mock_db.return_value.__aenter__.return_value

    await process_task("123", db)

    mock_task.get.assert_awaited_once_with("123", db)
    mock_logger.warning.assert_called_with("Task 123 not found.")

@pytest.mark.asyncio
async def test_process_task_already_processed(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "completed"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value

    await process_task("123", db)

    mock_task.get.assert_awaited_once_with("123", db)
    mock_logger.warning.assert_called_with("Task 123 already processed or canceled.")

@pytest.mark.asyncio
async def test_process_task_success(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "pending"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value

    await process_task("123", db)

    mock_task.get.assert_awaited_once_with("123", db)
    assert task.status == "completed"
    db.commit.assert_awaited()
    mock_logger.info.assert_called_with("Task 123 completed.")

@pytest.mark.asyncio
async def test_process_task_exception(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "pending"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value
    db.commit = mock.AsyncMock(side_effect=Exception("commit error"))

    await process_task("123", db)

    mock_task.get.assert_awaited_once_with("123", db)
    db.commit.assert_awaited()
    db.rollback.assert_awaited()
    mock_logger.error.assert_called_with("Task 123 processing error: commit error")
