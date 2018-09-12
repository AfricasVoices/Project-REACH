#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 05_update_messages_with_surveys.sh <user> <data-root>"
    echo "Updates messages with "
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../update_messages_with_surveys

mkdir -p "$DATA_ROOT/05 Messages & Raw Surveys"

SHOW="esc4jmcna_activation"

echo "Joining $SHOW with surveys"

sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW.json" \
    "$DATA_ROOT/04 Raw Contacts/contacts.json" "$DATA_ROOT/05 Messages & Raw Surveys/$SHOW.json"
