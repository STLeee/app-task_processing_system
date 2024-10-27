from fastapi import HTTPException
import pytest
from unittest import mock
from fastapi.testclient import TestClient
import pytest_asyncio
from app.api.task_api import router
from app.schemas import TASK_STATUS_CANCELED, TASK_STATUS_PENDING

client = TestClient(router)

@pytest_asyncio.fixture
def mock_task():
    with mock.patch('app.api.task_api.Task') as MockTask:
        yield MockTask

@pytest_asyncio.fixture
def mock_enqueue_task():
    with mock.patch('app.api.task_api.enqueue_task') as MockEnqueueTask:
        yield MockEnqueueTask

@pytest_asyncio.fixture
def mock_logger():
    with mock.patch('app.api.task_api.logger') as MockLogger:
        yield MockLogger

def test_create_task(mock_task, mock_enqueue_task, mock_logger):
    task_data = {"content": "Test task"}
    mock_task.create.return_value = mock_task
    mock_task.id = "123"
    mock_task.content = "Test task"
    mock_task.status = TASK_STATUS_PENDING
    mock_task.save = mock.AsyncMock()

    response = client.post("/task", json=task_data)

    assert response.status_code == 201
    assert response.json()["id"] == "123"
    mock_task.create.assert_called_once_with(content="Test task")
    mock_task.save.assert_awaited_once()
    mock_enqueue_task.assert_awaited_once_with("123")
    mock_logger.info.assert_called_with("Task created with ID: 123")

def test_get_task(mock_task, mock_logger):
    mock_task.get = mock.AsyncMock(return_value=mock_task)
    mock_task.id = "123"
    mock_task.content = "Test task"
    mock_task.status = TASK_STATUS_PENDING

    # test successful response
    response = client.get("/task/123")

    assert response.status_code == 200
    assert response.json()["id"] == "123"
    mock_task.get.assert_awaited_once_with("123")
    mock_logger.error.assert_not_called()

    mock_task.get = mock.AsyncMock(return_value=None)

    # test task not found
    with pytest.raises(HTTPException) as err:
        client.get("/task/456")

        assert err.value.status_code == 404
        assert err.value.detail == "Task not found"
        mock_task.get.assert_awaited_with("456")
        mock_logger.error.assert_called_with("Task 456 not found.")

def test_cancel_task(mock_task, mock_logger):
    mock_task.get = mock.AsyncMock(return_value=mock_task)
    mock_task.id = "123"
    mock_task.content = "Test task"
    mock_task.status = TASK_STATUS_PENDING
    mock_task.update = mock.AsyncMock()

    # test successful response
    response = client.patch("/task/123/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == TASK_STATUS_CANCELED
    mock_task.get.assert_awaited_once_with("123")
    mock_task.update.assert_awaited_once()
    mock_logger.info.assert_called_with("Task 123 canceled.")

    mock_task.get = mock.AsyncMock(return_value=None)

    # test task not found
    with pytest.raises(HTTPException) as err:
        client.patch("/task/456/cancel")

        assert err.value.status_code == 404
        assert err.value.detail == "Task not found"
        mock_task.get.assert_awaited_with("456")
        mock_logger.error.assert_called_with("Task 456 not found.")

    # test task already processing
    mock_task.get = mock.AsyncMock(return_value=mock_task)
    mock_task.status = "completed"

    # test task not found
    with pytest.raises(HTTPException) as err:
        client.patch("/task/789/cancel")

        assert err.value.status_code == 400
        assert err.value.json()["detail"] == "Task cannot be canceled"
        mock_task.get.assert_awaited_with("789")
        mock_logger.warning.assert_called_with("Task 789 cannot be canceled as it is already completed.")
