# Task Processing System

- [Task Processing System](#task-processing-system)
  - [Project Architecture](#project-architecture)
  - [How to Run the Application Using Docker or Docker Compose](#how-to-run-the-application-using-docker-or-docker-compose)
  - [How to Execute Tests](#how-to-execute-tests)
  - [Assumptions or Additional Design Decisions](#assumptions-or-additional-design-decisions)
  - [API Description](#api-description)
    - [Create Task API](#create-task-api)
    - [Get Task API](#get-task-api)
    - [Cancel Task API](#cancel-task-api)
    - [Health Check API](#health-check-api)
  - [Consumer for Processing Messages](#consumer-for-processing-messages)

## Project Architecture

The Task Processing System is structured as follows:

- **app/**: Contains the main application code.
  - **api/**: API-related code.
  - **consumer/**: Consumer-related code.
  - **core/**: Core functionalities and configurations.
  - **db/**: Database-related code.
  - **queue/**: Queue-related code.
  - **utils/**: Utility functions.
- **config/**: Configuration files for the application.
  - **supervisord.conf**: Configuration for Supervisor.
  - **uvicorn.log.conf.yml**: Logging configuration for Uvicorn.
- **tests/**: Test cases for the application.
- **Dockerfile**: Dockerfile for building the application image.
- **docker-compose.yml**: Docker Compose configuration for the application.
- **docker-compose.test.yml**: Docker Compose configuration for running tests.
- **.env.dev**: Environment variables for development.
- **.env.test**: Environment variables for testing.
- **makefile**: Makefile for common tasks.

## How to Run the Application Using Docker or Docker Compose

1. **Build the Docker image**:
    ```sh
    make build
    ```

2. **Start the application**:
    ```sh
    make start
    ```

3. **Stop the application**:
    ```sh
    make stop
    ```

## How to Execute Tests

To run the tests, use the following command:
```sh
make test
```

This command will use Docker Compose to spin up the necessary services and execute the tests defined in the tests/ directory.

## Assumptions or Additional Design Decisions

- **Database**: PostgreSQL is used as the database, and its data is stored in the data/postgres directory.
- **Queue**: Redis is used as the queue system.
- **Environment Variables**: The application uses environment variables defined in .env.dev and .env.test for configuration.
- **Logging**: Logging is configured using config/uvicorn.log.conf.yml to output logs to stdout and stderr.
- **Supervisor**: Supervisor is used to manage the Uvicorn process, as configured in config/supervisord.conf.
- **Health Checks**: Health checks are configured for the app, db, and redis services in docker-compose.yml.
- **Scalable**: The architecture allows adjustable worker counts for parallel processing, with the flexibility to deploy the server and consumer services separately in the future.

## API Description

The Task Processing System provides APIs for message handling using **FastAPI**. You can find the implementation of these APIs in the [app/api/task_api.py](app/api/task_api.py) file.

### Create Task API

    - **Endpoint**: `/task`
    - **Method**: `POST`
    - **Description**: Receives a message payload and enqueues it into a message queue (e.g., Redis, RabbitMQ, Kafka). It also creates a new `task` in the database and sets the `status` of the `task` to `pending`.
    - **Request Body**:
        ```json
        {
            "content": "string"
        }
        ```
    - **Response**:
        ```json
        {
            "id": "string",
            "content": "string",
            "status": "pending",
            "created_at": "2024-10-28T08:04:08.990161Z",
            "updated_at": null
        }
        ```
    - **Status Codes**:
        - `201 Created`: Task successfully created and enqueued.
        - `500 Internal Server Error`: Error occurred during task creation or enqueuing.

### Get Task API

    - **Endpoint**: `/task/{task_id}`
    - **Method**: `GET`
    - **Description**: Get Task date.
    - **Path Parameters**:
        - `task_id`: The ID of the task.
    - **Response**:
        ```json
        {
            "id": "string",
            "content": "string",
            "status": "pending",
            "created_at": "2024-10-28T08:04:08.990161Z",
            "updated_at": null
        }
        ```
    - **Status Codes**:
        - `200 OK`: Task successfully found in database.
        - `404 Not Found`: Task not found.

### Cancel Task API

    - **Endpoint**: `/task/{task_id}/cancel`
    - **Method**: `PATCH`
    - **Description**: Cancels a task if its status is still `pending` or `processing`. Once the task has been marked as `completed`, cancellation is not allowed.
    - **Path Parameters**:
        - `task_id`: The ID of the task to be canceled.
    - **Response**:
        ```json
        {
            "id": "string",
            "content": "string",
            "status": "canceled",
            "created_at": "2024-10-28T08:04:08.990161Z",
            "updated_at": "2024-10-28T08:04:12.067154Z"
        }
        ```
    - **Status Codes**:
        - `200 OK`: Task successfully canceled.
        - `404 Not Found`: Task not found.
        - `400 Bad Request`: Task cannot be canceled because it is already completed.

### Health Check API

- **Endpoint**: `/health`
- **Method**: `GET`
- **Description**: Checks the health status of the application.
- **Response**:
    ```json
    {
        "status": "ok"
    }
    ```
- **Status Codes**:
    - `200 OK`: Application is healthy.

## Consumer for Processing Messages

The consumer component reads messages from the queue and processes them asynchronously. Upon receiving a task, the consumer performs the following steps:

1. Updates the task's `status` to `processing`.
2. Sleeps for 3 seconds to simulate task processing.
3. After 3 seconds, updates the corresponding task in the database to set its status to `completed`.
