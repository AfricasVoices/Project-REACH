#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 05_06_survey_auto_code.sh <user> <data-root>"
    echo "Merges and cleans the raw demographic and practice surveys, and exports to Coda files for manual verification/coding"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../survey_auto_code

mkdir -p "$DATA_ROOT/06 Auto-Coded"
mkdir -p "$DATA_ROOT/07 Coda Files"

sh docker-run.sh "$USER" "$DATA_ROOT/05 Messages & Raw Surveys/esc4jmcna_activation.json" \
    "$DATA_ROOT/09 Coded Coda Files/" "$DATA_ROOT/06 Auto-Coded/esc4jmcna_activation.json" "$DATA_ROOT/07 Coda Files/"
