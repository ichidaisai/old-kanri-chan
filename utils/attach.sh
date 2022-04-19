#!/bin/sh
CONTAINER_ID=$(docker-compose ps -q app)
docker exec -it $CONTAINER_ID sh -c "cd /workspace/app && /bin/bash"