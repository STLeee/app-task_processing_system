APP_NAME=task-processing-system
APP_VERSION=develop

build:
	docker build \
		--platform linux/amd64 \
		-t $(APP_NAME):$(APP_VERSION) \
		.

run_sh:
	docker run -it --rm \
		--platform linux/amd64 \
		--name $(APP_NAME) \
		$(APP_NAME):$(APP_VERSION) \
		/bin/bash

start:
	docker-compose up

stop:
	docker-compose down

test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
