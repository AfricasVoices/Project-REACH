#!/bin/bash

set -e

IMAGE_NAME=esc4jmcna-analysis-file

# Check that the correct number of arguments were provided.
if [ $# -ne 6 ]; then
    echo "Usage: sh docker-run.sh <user> <messages-input-path> <survey-input-path> <json-output-path> <messages-csv-output-path> <individuals-csv-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_MESSAGES_DIR=$2
INPUT_SURVEY=$3
OUTPUT_JSON=$4
OUTPUT_MESSAGES_CSV=$5
OUTPUT_INDIVIDUALS_CSV=$6

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
docker cp "$INPUT_MESSAGES_DIR/." "$container:/data/messages-input"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_MESSAGES_CSV")"
docker cp "$container:/data/output-messages.csv" "$OUTPUT_MESSAGES_CSV"

mkdir -p "$(dirname "$OUTPUT_INDIVIDUALS_CSV")"
docker cp "$container:/data/output-individuals.csv" "$OUTPUT_INDIVIDUALS_CSV"
