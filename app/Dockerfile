# Install dependencies using multi-stage build
FROM python:3.9.10-bullseye AS builder

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

# Set timezone
RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Runner
FROM python:3.9.10-bullseye AS runner

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /etc/localtime /etc/localtime

# Copy application from host
WORKDIR /app
COPY ./ /app

CMD cd /app && python main.py