#!/bin/bash

# Use argument if given, otherwise current directory
target_dir="${1:-$PWD}"

echo "Running dot_clean continuously on: $target_dir"
echo "Press CTRL+C to stop."

while true; do
    dot_clean "$target_dir"
    echo "dot_clean completed at $(date)"
    sleep 5  # Wait 5 seconds before running again (adjust if you want)
done
