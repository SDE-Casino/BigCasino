#!/bin/bash

# Script to clear all tables from the memory database
# Usage: ./clear_postgres_tables.sh

echo "Clearing PostgreSQL tables..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if the memory_db container is running
if ! docker ps | grep -q "bigcasino-memory_db-1"; then
    echo "Error: memory_db container is not running. Please start the services with 'docker-compose up -d'"
    exit 1
fi

# List current tables before deletion
echo "Current tables in the database:"
docker exec bigcasino-memory_db-1 psql -U postgres -d memory_db -c "\dt"

# Drop all tables (cards first due to foreign key constraint, then games)
echo "Dropping tables..."
docker exec bigcasino-memory_db-1 psql -U postgres -d memory_db -c "DROP TABLE IF EXISTS cards; DROP TABLE IF EXISTS games;"

# Verify tables are deleted
echo "Verifying tables are deleted:"
docker exec bigcasino-memory_db-1 psql -U postgres -d memory_db -c "\dt"

echo "All tables have been successfully cleared from the memory database."