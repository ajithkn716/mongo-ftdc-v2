#!/bin/bash
#
# Author: najith716@gmail.com
# Description: Process MongoDB FTDC metric files, decode and parse them using Go and Python scripts.
#

set -euo pipefail

#############################################
# Cleanup on Ctrl+C
#############################################
cleanup() {
    echo
    echo "Shutting down Docker Compose..."
    docker-compose down
    echo "Script terminated."
    exit 0
}

trap cleanup SIGINT

#############################################
# Usage Info
#############################################
usage() {
    echo "Usage: $0 <metrics_directory>"
    echo
    echo "Example:"
    echo "  $0 /data/metrics"
    exit 1
}

#############################################
# Validate Input
#############################################
if [[ $# -ne 1 ]]; then
    usage
fi

METRICS_DIR="$1"
if [[ ! -d "$METRICS_DIR" ]]; then
    echo "Error: Directory '$METRICS_DIR' not found."
    exit 1
fi

#############################################
# Process a single metric file with progress
#############################################
process_file() {
    local idx="$1"
    local total="$2"
    local metric_file="$3"

    if [[ ! -f "$metric_file" ]]; then
        echo "[$idx/$total] No metric file found: $metric_file"
        return
    fi

    local timestamp temp_json
    timestamp=$(basename "$metric_file" | cut -d'-' -f2-3)
    temp_json="temp_${timestamp}.json"

    echo "[$idx/$total] Processing: $(basename "$metric_file")"

    # Decode FTDC using Go binary
    ./ftdc_decoder -input "$metric_file" -output "$temp_json" -idx "$idx" -total "$total"

    if [[ -f "$temp_json" ]]; then
        # Parse JSON using Python
        python3 /scripts/ftdc_parser.py "$temp_json" "$idx" "$total"
        rm -f "$temp_json"
    else
        echo "[$idx/$total] Warning: Failed to create $temp_json for $metric_file"
    fi
}

export -f process_file

#############################################
# Main Execution
#############################################
echo
echo "☕ This may take a while... please wait."
echo

# Determine number of files to process in parallel
: "${MAX_FILE_PROCESS:=1}"
echo "Using $MAX_FILE_PROCESS file(s) in parallel for processing"

# Get list of metric files sorted
mapfile -t METRIC_FILES < <(find "$METRICS_DIR" -type f -name 'metrics.*' | sort)
TOTAL_FILES=${#METRIC_FILES[@]}

# Build NUL-separated input for xargs
for idx in "${!METRIC_FILES[@]}"; do
    file="${METRIC_FILES[$idx]}"
    printf "%s\0%s\0%s\0" "$((idx+1))" "$TOTAL_FILES" "$file"
done | xargs -0 -n 3 -P "$MAX_FILE_PROCESS" bash -c 'process_file "$0" "$1" "$2"'

echo
echo "All files processed successfully!"

echo
echo "Generating dashboard URL..."
python3 /scripts/get_url.py

echo
echo "Processing complete."
echo "Press Ctrl-C when you’re done analyzing the dashboard."

#############################################
# Keep container alive
#############################################
while true; do
    sleep 1
done
