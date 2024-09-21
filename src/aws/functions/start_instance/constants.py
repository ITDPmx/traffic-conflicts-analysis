region = 'us-east-1'
DOCKER_COMPOSE_COMMAND = "docker compose --file  traffic-conflicts-analysis/src/docker-compose.yml up --build --detach"

instance_ids = ["i-02a33facac910baba"]

CONTAINER_STATUS_COMMAND = "docker inspect --format='{{{{.State.Status}}}}' {container_name}"
PORT_STATUS_COMMAND = "netstat -tuln | grep :{port}"

DOCKER_UP_STATUS = "running"

# Define the services and their ports
services = {
    "bev": 8000,
    "ttc": 8001
}