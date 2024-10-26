FROM python:3.10-slim

WORKDIR /tps

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy project
COPY ./app ./app
COPY ./script ./script

# expose port
EXPOSE 8000

# set environment variables
ENV WORKERS=1

# start server
CMD ["bash", "-x", "./script/start.sh"]
