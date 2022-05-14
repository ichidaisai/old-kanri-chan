# Install dependencies using multi-stage build
FROM python:3.9.10-bullseye

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Copy application from host
WORKDIR /app
COPY ./ /app
RUN pip install -r ./requirements.txt

CMD cd /app && python main.py