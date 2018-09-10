#!/usr/bin/env bash

set -e

if [ $# -ne 5 ]; then
    echo "Usage: sh 04_fetch_surveys.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>"
    echo "Downloads radio show answers from each show"
    exit
fi

USER=$1
RP_DIR=$2
RP_SERVER=$3
RP_TOKEN=$4
DATA_ROOT=$5

TEST_CONTACTS_PATH="$(pwd)/test_contacts.json"

cd "$RP_DIR"

mkdir -p "$DATA_ROOT/04 Raw Surveys"

SURVEYS=(
    "esc4jmcna_demog"
    "esc4jmcna_evaluation"
    )

for SURVEY in ${SURVEYS[@]}
do
    echo "Exporting survey $SURVEY"

    sh docker-run.sh  --flow-name "$SURVEY" --test-contacts-path "$TEST_CONTACTS_PATH" \
        "$RP_SERVER" "$RP_TOKEN" "$USER" latest-only \
        "$DATA_ROOT/00 UUIDs/phone_uuids.json" "$DATA_ROOT/04 Raw Surveys/$SURVEY.json"
done
