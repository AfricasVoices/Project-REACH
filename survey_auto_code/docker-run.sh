#!/bin/bash

set -e

IMAGE_NAME=esc4jmcna-survey-auto-code

# Check that the correct number of arguments were provided.
if [ $# -ne 6 ]; then
    echo "Usage: sh docker-run.sh <user> <data-input-path> <prev-coded-path> <phone-uuid-table> <json-output-path> <coded-output-path>"
    echo "Note: The file at <prev-coded-output> need not exist for this script to run"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
PREV_CODED_DIR=$3
PHONE_UUID_TABLE=$4
OUTPUT_JSON=$5
CODED_DIR=$6

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
docker cp "$INPUT_JSON" "$container:/data/input.json"
if [ -d "$PREV_CODED_DIR" ]; then
    docker cp "$PREV_CODED_DIR" "$container:/data/prev-coded"
fi
docker cp "$PHONE_UUID_TABLE" "$container:/data/phone-uuid-table.json"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$CODED_DIR"
docker cp "$container:/data/coded/." "$CODED_DIR"
