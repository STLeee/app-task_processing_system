import pytest
from unittest import mock
from fastapi import HTTPException
import pytest_asyncio
from app.api.task_api import create_task, get_task, cancel_task
from app.schemas import TaskCreate

@pytest_asyncio.fixture
def mock_task():
    with mock.patch('app.api.task_api.Task') as MockTask:
        yield MockTask

@pytest_asyncio.fixture
def mock_db():
    with mock.patch('app.api.task_api.async_session') as MockSession:
        yield MockSession

@pytest_asyncio.fixture
def mock_logger():
    with mock.patch('app.api.task_api.logger') as MockLogger:
        yield MockLogger

@pytest.mark.asyncio
async def test_create_task_success(mock_task, mock_db, mock_logger):
    task_create = TaskCreate(content="test content")
    new_task = mock.Mock()
    mock_task.return_value = new_task
    db = mock_db.return_value.__aenter__.return_value

    with mock.patch('app.api.task_api.enqueue_task'):
        result = await create_task(task_create, db)

        db.add.assert_called_once_with(new_task)
        db.commit.assert_awaited()
        db.refresh.assert_awaited_with(new_task)
        mock_logger.info.assert_called_with(f"Task created with ID: {new_task.id}")
        assert result == new_task

@pytest.mark.asyncio
async def test_create_task_db_error(mock_task, mock_db, mock_logger):
    task_create = TaskCreate(content="test content")
    new_task = mock.Mock()
    mock_task.return_value = new_task
    db = mock_db.return_value.__aenter__.return_value
    db.commit = mock.AsyncMock(side_effect=Exception("commit error"))

    with pytest.raises(HTTPException) as exc_info:
        await create_task(task_create, db)

    assert exc_info.value.status_code == 500
    db.add.assert_called_once_with(new_task)
    db.commit.assert_awaited()
    db.rollback.assert_awaited()
    mock_logger.error.assert_called_with("Task creation error: commit error")

@pytest.mark.asyncio
async def test_create_task_enqueue_error(mock_task, mock_db, mock_logger):
    task_create = TaskCreate(content="test content")
    new_task = mock.Mock()
    mock_task.return_value = new_task
    db = mock_db.return_value.__aenter__.return_value
    db.commit = mock.AsyncMock()
    db.refresh = mock.AsyncMock()
    with mock.patch('app.api.task_api.enqueue_task', mock.AsyncMock(side_effect=Exception("enqueue error"))):
        with pytest.raises(HTTPException) as exc_info:
            await create_task(task_create, db)

        assert exc_info.value.status_code == 500
        db.add.assert_called_once_with(new_task)
        db.commit.assert_awaited()
        db.refresh.assert_awaited_with(new_task)
        db.delete.assert_called_once_with(new_task)
        mock_logger.error.assert_called_with("Task creation error: enqueue error")

@pytest.mark.asyncio
async def test_get_task_not_found(mock_task, mock_db, mock_logger):
    mock_task.get = mock.AsyncMock(return_value=None)
    db = mock_db.return_value.__aenter__.return_value

    with pytest.raises(HTTPException) as exc_info:
        await get_task("123", db)

    assert exc_info.value.status_code == 404
    mock_task.get.assert_awaited_once_with("123", db)
    mock_logger.error.assert_called_with("Task 123 not found.")

@pytest.mark.asyncio
async def test_cancel_task_not_found(mock_task, mock_db, mock_logger):
    mock_task.get = mock.AsyncMock(return_value=None)
    db = mock_db.return_value.__aenter__.return_value

    with pytest.raises(HTTPException) as exc_info:
        await cancel_task("123", db)

    assert exc_info.value.status_code == 404
    mock_task.get.assert_awaited_once_with("123", db)
    mock_logger.error.assert_called_with("Task 123 not found.")

@pytest.mark.asyncio
async def test_cancel_task_already_completed(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "completed"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value

    with pytest.raises(HTTPException) as exc_info:
        await cancel_task("123", db)

    assert exc_info.value.status_code == 400
    mock_task.get.assert_awaited_once_with("123", db)
    mock_logger.warning.assert_called_with("Task 123 cannot be canceled as it is already completed.")

@pytest.mark.asyncio
async def test_cancel_task_success(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "pending"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value

    await cancel_task("123", db)

    mock_task.get.assert_awaited_once_with("123", db)
    assert task.status == "canceled"
    db.commit.assert_awaited()
    db.refresh.assert_awaited_with(task)
    mock_logger.info.assert_called_with("Task 123 canceled.")

@pytest.mark.asyncio
async def test_cancel_task_exception(mock_task, mock_db, mock_logger):
    task = mock.Mock()
    task.status = "pending"
    mock_task.get = mock.AsyncMock(return_value=task)
    db = mock_db.return_value.__aenter__.return_value
    db.commit = mock.AsyncMock(side_effect=Exception("commit error"))

    with pytest.raises(HTTPException) as exc_info:
        await cancel_task("123", db)

    assert exc_info.value.status_code == 500
    mock_task.get.assert_awaited_once_with("123", db)
    db.commit.assert_awaited()
    mock_logger.error.assert_called_with("Task 123 cancel error: commit error")
