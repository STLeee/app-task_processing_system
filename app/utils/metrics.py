from prometheus_client import Counter, Gauge, Histogram

metrics_task_status = Gauge("task_status", "Task status", ["status"])

metrics_task_create_request_count = Counter("task_create_request_count", "Task create request counter")
metrics_task_create_success_count = Counter("task_create_success_count", "Task create success counter")
metrics_task_create_fail_count = Counter("task_create_fail_count", "Task create fail counter")
metrics_task_get_request_count = Counter("task_get_request_count", "Task get request counter")
metrics_task_cancel_request_count = Counter("task_cancel_request_count", "Task cancel request counter")
metrics_task_cancel_success_count = Counter("task_cancel_success_count", "Task cancel success counter")
metrics_task_cancel_fail_count = Counter("task_cancel_fail_count", "Task cancel fail counter")

metrics_task_processing_duration = Histogram("task_processing_duration", "Task processing duration")
metrics_task_processing_success_count = Counter("task_processing_success_count", "Task processing success counter")
metrics_task_processing_fail_count = Counter("task_processing_fail_count", "Task processing fail counter")