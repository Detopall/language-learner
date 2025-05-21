#!/bin/bash

# Define the container name
COMPOSE_FILE=docker-compose.yaml

# Define the help message
HELP_MESSAGE="Usage:
  $0 start        Start the container
  $0 stop         Stop the container
  $0 rm           Remove the container
  $0 rm-all       Remove all containers and volumes
  $0 logs         Show logs for the container
  $0 help         Show this help message
"

# Define the functions
start() {
  docker compose up -d
}

stop() {
  docker compose down
}

rm() {
  docker compose -f $COMPOSE_FILE down
}

rm-all() {
  docker compose -f $COMPOSE_FILE down
  docker compose -f $COMPOSE_FILE down --rmi all
}

logs() {
  docker compose logs
}

help() {
  echo "$HELP_MESSAGE"
}

# Parse the command-line arguments
case $1 in
  start)
    start
    ;;
  stop)
    stop
    ;;
  rm)
    rm
    ;;
  rm-all)
    rm-all
    ;;
  logs)
    logs
    ;;
  help)
    help
    ;;
  *)
    echo "Unknown command: $1"
    help
    ;;
esac
