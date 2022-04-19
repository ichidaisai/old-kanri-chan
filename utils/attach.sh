#!/bin/sh
CONTAINER_ID=$(docker-compose ps -q app)
docker exec -it $CONTAINER_ID bash