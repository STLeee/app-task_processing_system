from prometheus_client import Counter, Gauge, Histogram

# task status
metrics_task_status = Gauge("task_status", "Task status", ["status"])

# task operation
metrics_task_create_request_count = Counter("task_create_request_count", "Task create request counter")
metrics_task_create_success_count = Counter("task_create_success_count", "Task create success counter")
metrics_task_create_fail_count = Counter("task_create_fail_count", "Task create fail counter")
metrics_task_get_request_count = Counter("task_get_request_count", "Task get request counter")
metrics_task_cancel_request_count = Counter("task_cancel_request_count", "Task cancel request counter")
metrics_task_cancel_success_count = Counter("task_cancel_success_count", "Task cancel success counter")
metrics_task_cancel_fail_count = Counter("task_cancel_fail_count", "Task cancel fail counter")

# task processing
metrics_task_processing_duration = Histogram("task_processing_duration", "Task processing duration")
metrics_task_processing_success_count = Counter("task_processing_success_count", "Task processing success counter")
metrics_task_processing_fail_count = Counter("task_processing_fail_count", "Task processing fail counter")

# queue
metrics_queue_length = Gauge("queue_length", "Queue length")
metrics_queue_push_count = Counter("queue_push_count", "Queue push counter")
metrics_queue_push_fail_count = Counter("queue_push_fail_count", "Queue push fail counter")
metrics_queue_pop_count = Counter("queue_pop_count", "Queue pop counter")
metrics_queue_pop_fail_count = Counter("queue_pop_fail_count", "Queue pop fail counter")
