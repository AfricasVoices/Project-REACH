#!/usr/bin/env bash

set -e

if [ $# -ne 5 ]; then
    echo "Usage: ./2_fetch_raw_data.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>"
    echo "Downloads the radio show answers from each show, as well as all the contacts data"
    exit
fi

USER=$1
RP_DIR=$2
RP_SERVER=$3
RP_TOKEN=$4
DATA_ROOT=$5

TEST_CONTACTS_PATH="$(pwd)/test_contacts.json"

./checkout_rapid_pro_tools.sh "$RP_DIR"

mkdir -p "$DATA_ROOT/Raw Data"

SHOWS=(
    "esc4jmcna_activation"
    )

# Export radio show messages
cd "$RP_DIR/fetch_runs"
for SHOW in ${SHOWS[@]}
do
    echo "Exporting show $SHOW"

    ./docker-run.sh --flow-name "$SHOW" --test-contacts-path "$TEST_CONTACTS_PATH" \
        "$RP_SERVER" "$RP_TOKEN" "$USER" all \
        "$DATA_ROOT/UUIDs/phone_uuids.json" "$DATA_ROOT/Raw Data/$SHOW.json"
done

# Export contacts
cd "$RP_DIR/fetch_contacts"
echo "Exporting contacts"
./docker-run.sh --test-contacts-path "$TEST_CONTACTS_PATH" "$RP_SERVER" "$RP_TOKEN" "$USER" \
    "$DATA_ROOT/UUIDs/phone_uuids.json" "$DATA_ROOT/Raw Data/contacts.json"

