#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 07_08_join_messages_surveys.sh <user> <data-root>"
    echo "Joins messages and demographic surveys on phone id, and produces CSV files for analysis"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../join_messages_surveys

mkdir -p "$DATA_ROOT/07 Joined Data"
mkdir -p "$DATA_ROOT/08 Joined Raw Data CSVs"

SHOW="esc4jmcna_activation"

echo "Joining $SHOW with surveys"

sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW.json" \
    "$DATA_ROOT/04 Raw Surveys/contacts.json" "delete-me" "delete-me" \
    "$DATA_ROOT/07 Joined Data/$SHOW.json" "$DATA_ROOT/08 Joined Raw Data CSVs/$SHOW.csv"
