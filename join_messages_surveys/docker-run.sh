#!/bin/bash

set -e

IMAGE_NAME=esc4jmcna-join-messages-surveys

# Check that the correct number of arguments were provided.
if [ $# -ne 7 ]; then
    echo "Usage: sh docker-run.sh <user> <messages-input-file> <survey-input-file> <flow-name> <variable-name> <output-file> <output-csv>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_MESSAGES=$2
INPUT_SURVEY=$3
FLOW_NAME=$4
VARIABLE_NAME=$5
OUTPUT_JSON=$6
OUTPUT_CSV=$7

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" --env FLOW_NAME="$FLOW_NAME" --env VARIABLE_NAME="$VARIABLE_NAME" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_MESSAGES" "$container:/data/messages-input.json"
docker cp "$INPUT_SURVEY" "$container:/data/survey-input.json"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_CSV")"
docker cp "$container:/data/output.csv" "$OUTPUT_CSV"
