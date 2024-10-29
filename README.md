# Task Processing System

- [Task Processing System](#task-processing-system)
  - [Project Architecture](#project-architecture)
  - [Environment Variable Description](#environment-variable-description)
    - [Common Environment Variables](#common-environment-variables)
  - [How to Run the Application Using Docker or Docker Compose](#how-to-run-the-application-using-docker-or-docker-compose)
  - [How to Execute Tests](#how-to-execute-tests)
  - [API Description](#api-description)
    - [Create Task API](#create-task-api)
    - [Get Task API](#get-task-api)
    - [Cancel Task API](#cancel-task-api)
    - [Health Check API](#health-check-api)
  - [Consumer for Processing Messages](#consumer-for-processing-messages)
  - [Metrics System](#metrics-system)
    - [API](#api)
    - [Prometheus](#prometheus)
      - [How to Access Prometheus](#how-to-access-prometheus)
    - [Example Metrics](#example-metrics)
    - [Grafana](#grafana)
    - [How to Access Grafana](#how-to-access-grafana)
  - [Assumptions or Additional Design Decisions](#assumptions-or-additional-design-decisions)
  - [Potential Improvements](#potential-improvements)

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
  - **grafana/**: Grafana configuration files.
  - **prometheus.yml**: Configuration for Prometheus.
  - **supervisord.conf**: Configuration for Supervisor.
  - **uvicorn.log.conf.yml**: Logging configuration for Uvicorn.
- **tests/**: Test cases for the application.
- **Dockerfile**: Dockerfile for building the application image.
- **docker-compose.yml**: Docker Compose configuration for the application.
- **docker-compose.test.yml**: Docker Compose configuration for running tests.
- **.env.dev**: Environment variables for development.
- **.env.test**: Environment variables for testing.
- **makefile**: Makefile for common tasks.

## Environment Variable Description

The Task Processing System uses several environment variables to manage its configuration. These variables are defined in `.env.dev` for development and `.env.test` for testing.

### Common Environment Variables

- **APP_ENV**
  - **Description**: Specifies the environment in which the application is running.
  - **Default**: `dev`
  - **Example**: `APP_ENV=dev`

- **LOG_LEVEL**
  - **Description**: Sets the logging level for the application.
  - **Default**: `debug`
  - **Example**: `LOG_LEVEL=debug`

- **LOG_FILE_PATH**
  - **Description**: Specifies the path to the log file.
  - **Default**: `logs/app.log`
  - **Example**: `LOG_FILE_PATH=logs/app.log`

- **DATABASE_URL**
  - **Description**: URL for connecting to the database.
  - **Default**: `postgresql+asyncpg://username:password@localhost:5432/db`
  - **Example**: `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/task_db`

- **REDIS_HOST**
  - **Description**: Hostname for the Redis server.
  - **Default**: `localhost`
  - **Example**: `REDIS_HOST=redis`

- **TASK_CONSUMER_WORKERS**
  - **Description**: Number of worker processes for the task consumer.
  - **Default**: `1`
  - **Example**: `TASK_CONSUMER_WORKERS=4`

These environment variables are loaded and managed by the `Settings` class in [app/core/config.py](app/core/config.py).

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

## Metrics System

The Task Processing System includes a metrics system using Prometheus and Grafana for monitoring and visualization.

### API

- Metrics Endpoint: `/metrics`
  - Method: `GET`
  - Description: Exposes application metrics for Prometheus to scrape.
  - Response: Prometheus metrics in plain text format.

### Prometheus

Prometheus is configured to scrape metrics from the application.

- Configuration File: [config/prometheus.yml](config/prometheus.yml)
- Scrape Interval: 15 seconds
- Scrape Target: `app:8000`

#### How to Access Prometheus

- Open your browser and go to `http://localhost:9090`

### Example Metrics

- Task Status Gauge: `task_status`
- Task Get Request Counter: `task_get_request_count`
- Task Create Request Counter: `task_create_request_count`
- Task Create Success Counter: `task_create_success_count`
- Task Create Fail Counter: `task_create_fail_count`
- Task Get Request Counter: `task_get_request_count`
- Task Cancel Request Counter: `task_cancel_request_count`
- Task Cancel Success Counter: `task_cancel_success_count`
- Task Cancel Fail Counter: `task_cancel_fail_count`
- Task Processing Duration Histogram: `task_processing_duration`
- Task Processing Success Counter: `task_processing_success_count`
- Task Processing Fail Counter: `task_processing_fail_count`

### Grafana

Grafana is used to visualize the metrics collected by Prometheus.

- Configuration Files:
  - Data Source: [config/grafana/datasource.yml](config/grafana/datasource.yml)
  - Dashboard:
    - [config/grafana/dashboards.yml](config/grafana/dashboards.yml)
    - [config/grafana/dashboards/task_processing_system.json](config/grafana/dashboards/task_processing_system.json)

### How to Access Grafana

- Open your browser and go to `http://localhost:3000`
- Default credentials: `admin`/`admin`

## Assumptions or Additional Design Decisions

- **Database**: PostgreSQL is used as the database.
- **Queue**: Redis is used as the queue system.
- **Supervisor**: Supervisor is used to manage the Uvicorn process, as configured in config/supervisord.conf.
- **Scalable**: The architecture allows adjustable worker counts for parallel processing, with the flexibility to deploy the server and consumer services separately in the future.

## Potential Improvements

- **Performance**
  - [ ] **Optimize Database Queries**: Use batch inserts/updates and efficient indexing for frequently accessed fields to reduce database load and speed up task processing.
  - [ ] **Implement Caching**: Cache frequently accessed task data or metadata in Redis to reduce database calls and improve response times.
  - [ ] **Connection Pooling**: Enable connection pooling for both Redis and the database to reduce the overhead of opening and closing connections.
  - [ ] **Batch Processing of Tasks**: Enable the consumer to process tasks in batches where appropriate, reducing the total number of I/O operations.
- **Development and Monitoring**
  - [] **Centralized Log Collection**: Centralized log aggregation and query capabilities (e.g. Loki), allowing efficient, structured log storage and real-time querying alongside Grafana metrics for enhanced monitoring and troubleshooting.
  - [] **Load and Stress Testing**: Conduct load tests to evaluate system behavior under heavy workloads, allowing for performance tuning before production deployment.
  - [] **Fault Injection**: Simulate network and service failures to verify system resilience and ensure the system handles Redis or database connection drops gracefully.
