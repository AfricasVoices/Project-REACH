#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 02_update_messages_with_surveys.sh <user> <data-root>"
    echo "Updates raw  messages with associated raw survey data"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../update_messages_with_surveys

mkdir -p "$DATA_ROOT/02 Raw Messages & Surveys"

SHOW="esc4jmcna_activation"

echo "Joining $SHOW with surveys"

sh docker-run.sh "$USER" "$DATA_ROOT/01 Raw Messages/$SHOW.json" \
    "$DATA_ROOT/04 Raw Contacts/contacts.json" "$DATA_ROOT/02 Raw Messages & Surveys/$SHOW.json"
