#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 09_apply_manual_codes.sh <user> <data-root>"
    echo "Applies codes from a directory of Coda files to survey responses"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../apply_manual_codes

mkdir -p "$DATA_ROOT/08 Coded Coda Files"
mkdir -p "$DATA_ROOT/09 Manually Coded"

sh docker-run.sh "$USER" "$DATA_ROOT/06 Auto-Coded/esc4jmcna_activation.json" \
    "$DATA_ROOT/08 Coded Coda Files" "$DATA_ROOT/09 Manually Coded/esc4jmcna_activation.json" \
    "$DATA_ROOT/03 Interface Files/"
