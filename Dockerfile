FROM python:3.10-slim

WORKDIR /tps

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN apt-get update
RUN apt-get install -y supervisor

# copy project
COPY ./app ./app
COPY ./script ./script
COPY ./config ./config
RUN mv ./config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# expose port
EXPOSE 8000

# set environment variables
ENV WORKERS=1

# start server
CMD ["supervisord", "-n"]
