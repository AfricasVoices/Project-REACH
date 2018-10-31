#!/bin/bash

set -e

IMAGE_NAME=reach-daap

# Check that the correct number of arguments were provided.
if [ $# -ne 11 ]; then
    echo "Usage: sh docker-run.sh <user> <phone-number-uuid-table-path> <messages-input-path> <survey-input-path> <prev-coded-dir> <json-output-path> <interface-output-dir> <icr-output-path> <coded-output-dir> <messages-output-csv> <individuals-output-csv>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_PHONE_UUID_TABLE=$2
INPUT_MESSAGES=$3
INPUT_SURVEYS=$4
PREV_CODED_DIR=$5
OUTPUT_JSON=$6
OUTPUT_INTERFACE=$7
OUTPUT_ICR=$8
OUTPUT_CODED_DIR=$9
OUTPUT_MESSAGES_CSV=${10}
OUTPUT_INDIVIDUALS_CSV=${11}

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
CMD="pipenv run python -u reach_pipeline.py $USER /data/phone-number-uuid-table-input.json
    /data/messages-input.json /data/survey-input.json /data/prev-coded
    /data/output.json /data/output-interface /data/output-icr.csv /data/coded
    /data/output-messages.csv /data/output-individuals.csv"
container="$(docker container create -w /app "$IMAGE_NAME" ${CMD})"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_PHONE_UUID_TABLE" "$container:/data/phone-number-uuid-table-input.json"
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

mkdir -p "$(dirname "$OUTPUT_INTERFACE")"
docker cp "$container:/data/output-interface" "$OUTPUT_INTERFACE"

mkdir -p "$(dirname "$OUTPUT_ICR")"
docker cp "$container:/data/output-icr.csv" "$OUTPUT_ICR"

mkdir -p "$OUTPUT_CODED_DIR"
docker cp "$container:/data/coded/." "$OUTPUT_CODED_DIR"

mkdir -p "$(dirname "$OUTPUT_MESSAGES_CSV")"
docker cp "$container:/data/output-messages.csv" "$OUTPUT_MESSAGES_CSV"

mkdir -p "$(dirname "$OUTPUT_INDIVIDUALS_CSV")"
docker cp "$container:/data/output-individuals.csv" "$OUTPUT_INDIVIDUALS_CSV"
