#!/bin/bash

set -e

IMAGE_NAME=reach-daap

# Check that the correct number of arguments were provided.
if [ $# -ne 7 ]; then
    echo "Usage: sh docker-run.sh <user> <messages-input-path> <survey-input-path> <prev-coded-dir> <json-output-path> <icr-output-path> <coded-output-dir>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_MESSAGES=$2
INPUT_SURVEYS=$3
PREV_CODED_DIR=$4
OUTPUT_JSON=$5
OUTPUT_ICR=$6
OUTPUT_CODED_DIR=$7

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
docker cp "$INPUT_MESSAGES" "$container:/data/messages-input.json"
docker cp "$INPUT_SURVEYS" "$container:/data/survey-input.json"
if [ -d "$PREV_CODED_DIR" ]; then
    docker cp "$PREV_CODED_DIR" "$container:/data/prev-coded"
fi

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_ICR")"
docker cp "$container:/data/output-icr.csv" "$OUTPUT_ICR"

mkdir -p "$OUTPUT_CODED_DIR"
docker cp "$container:/data/coded/." "$OUTPUT_CODED_DIR"
