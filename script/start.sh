#!bin/bash

# start server using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS}
