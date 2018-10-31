#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 3_generate_outputs.sh <user> <data-root>"
    echo "Downloads the radio show answers from each show, as well as all the contacts data"
    exit
fi

USER=$1
DATA_ROOT=$2

mkdir -p "$DATA_ROOT/Coded Coda Files"
mkdir -p "$DATA_ROOT/Outputs"

cd ..
sh docker-run.sh alexander "$DATA_ROOT/UUIDs/phone_uuids.json" \
    "$DATA_ROOT/Raw Data/esc4jmcna_activation.json" \
    "$DATA_ROOT/Raw Data/contacts.json" "$DATA_ROOT/Coded Coda Files/" \
    "$DATA_ROOT/Outputs/traced_data.json" "$DATA_ROOT/Outputs/Interface Files/" \
    "$DATA_ROOT/Outputs/esc4jmcna_activation_icr.csv" "$DATA_ROOT/Outputs/Coda Files/" \
    "$DATA_ROOT/Outputs/esc4jmcna_analysis_messages.csv" \
    "$DATA_ROOT/Outputs/esc4jmcna_analysis_individuals.csv"
