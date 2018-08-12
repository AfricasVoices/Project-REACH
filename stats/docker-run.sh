#!/bin/bash

set -e

IMAGE_NAME=wt-join-messages-surveys

# Check that the correct number of arguments were provided.
if [ $# -ne 3 ]; then
    echo "Usage: sh docker-run.sh <user> <survey-input-path> <stats-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_SURVEY=$2
OUTPUT_STATS=$3

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_SURVEY" "$container:/data/survey-input.json"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_STATS")"
docker cp "$container:/data/survey-stats.csv" "$OUTPUT_STATS"
