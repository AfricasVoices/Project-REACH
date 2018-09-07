#!/usr/bin/env bash

set -e

if [ $# -ne 5 ]; then
    echo "Usage: sh 04_fetch_contacts.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>"
    echo "Downloads all contacts from Rapid Pro"
    exit
fi

USER=$1
RP_DIR=$2
RP_SERVER=$3
RP_TOKEN=$4
DATA_ROOT=$5

TEST_CONTACTS_PATH="$(pwd)/test_contacts.json"

cd "$RP_DIR/fetch_contacts"

mkdir -p "$DATA_ROOT/04 Raw Contacts"

echo "Exporting contacts"

sh docker-run.sh --test-contacts-path "$TEST_CONTACTS_PATH" "$RP_SERVER" "$RP_TOKEN" "$USER" \
    "$DATA_ROOT/00 UUIDs/phone_uuids.json" "$DATA_ROOT/04 Raw Contacts/contacts.json"
