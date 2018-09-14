#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 12_analysis_dataset.sh <user> <data-root>"
    echo "Produces datasets suitable for final analysis"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../analysis_file

mkdir -p "$DATA_ROOT/12 Analysis"
mkdir -p "$DATA_ROOT/13 Analysis CSV"

sh docker-run.sh "$USER" "$DATA_ROOT/09 Manually Coded/" "$DATA_ROOT/09 Manually Coded/esc4jmcna_activation.json" \
    "$DATA_ROOT/12 Analysis/analysis.json" "$DATA_ROOT/13 Analysis CSV/esc4jmcna_analysis_messages.csv" \
    "$DATA_ROOT/13 Analysis CSV/esc4jmcna_analysis_individuals.csv"
