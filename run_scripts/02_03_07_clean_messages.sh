#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 02_03_07_clean_messages.sh <user> <data-root>"
    echo "Cleans radio show answers, and exports to The Interface and to Coda for analysis."
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../messages

mkdir -p "$DATA_ROOT/02 Clean Messages"
mkdir -p "$DATA_ROOT/03 Interface Files"
mkdir -p "$DATA_ROOT/07 Coda Files"

SHOWS=(
    "esc4jmcna_activation" S07E01_Humanitarian_Priorities
    )

for i in $(seq 0 $((${#SHOWS[@]} / 2 - 1)))
do
    SHOW="${SHOWS[2 * i]}"
    VARIABLE="${SHOWS[2 * i + 1]}"

    echo "Cleaning $SHOW"

    sh docker-run.sh "$USER" "$DATA_ROOT/01 Raw Messages/$SHOW.json" "$DATA_ROOT/08 Coded Coda Files/${SHOW}_coded.csv" \
        "$SHOW" "$VARIABLE" \
        "$DATA_ROOT/02 Clean Messages/$SHOW.json" "$DATA_ROOT/07 Coda Files/$SHOW.csv"
done
