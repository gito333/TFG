# dockerfile, Image, container# Use the official Python image from the Docker Hub
FROM python:3

# Copy the current directory contents into the container at /app
WORKDIR /app/src/
COPY ./src .
COPY ./requirements.txt ..
COPY ./config.json ..
COPY ./crontab /etc/cron.d/crontab

RUN pip install -r ../requirements.txt
RUN apt-get update && apt-get install -y cron
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
RUN touch /var/log/cron.log
RUN python main.py
CMD cron && tail -f /var/log/cron.log
