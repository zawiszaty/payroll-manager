#!/bin/bash
set -e

echo "Waiting for all services to be healthy..."

# Function to wait for a service to be healthy
wait_for_health() {
    local container_name=$1
    local timeout=$2
    local service_name=$3

    echo "Waiting for $service_name to be healthy..."

    local elapsed=0
    local interval=3

    while [ $elapsed -lt $timeout ]; do
        status=$(docker inspect --format="{{.State.Health.Status}}" "$container_name" 2>/dev/null || echo "not_found")

        if [ "$status" == "healthy" ]; then
            echo "✓ $service_name is healthy!"
            return 0
        fi

        echo "$service_name status: $status (${elapsed}s/${timeout}s)"
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo "✗ $service_name failed to become healthy within ${timeout}s"
    return 1
}

# Wait for each service
wait_for_health "payroll_postgres" 120 "PostgreSQL"
wait_for_health "payroll_rabbitmq" 60 "RabbitMQ"
wait_for_health "payroll_redis" 60 "Redis"

# Extra verification: test database connection
echo "Running final database verification..."
docker compose exec -T postgres psql -U payroll_user -d payroll_db -c "SELECT 1" > /dev/null
echo "✓ Database connection verified!"

echo "✓ All services are ready for testing!"
