FROM python:3.10-slim

WORKDIR /tps

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project
COPY ./app ./app

# expose port
EXPOSE 8000

# start server using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
