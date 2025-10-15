#!/bin/sh

set -e

js=$2
min=$3

lamdera make --optimize --no-wire --output="$js" "$1"
INITIAL_SIZE=$(wc -c < "$js")

swc "$js" --out-file "$min"

MINIFIED_SIZE=$(wc -c < "$min")
GZIPPED_SIZE=$(gzip -c "$min" | wc -c)

# Convert to human-readable format
INITIAL_HR=$(numfmt --to=iec-i --suffix=B "$INITIAL_SIZE")
MINIFIED_HR=$(numfmt --to=iec-i --suffix=B "$MINIFIED_SIZE")
GZIPPED_HR=$(numfmt --to=iec-i --suffix=B "$GZIPPED_SIZE")

# Display results with alignment
printf "%-18s %10s (%7s)  %s\n" "Initial size:" "$INITIAL_SIZE bytes" "${INITIAL_HR}" "$js"
printf "%-18s %10s (%7s)  %s\n" "Minified size:" "$MINIFIED_SIZE bytes" "${MINIFIED_HR}" "$min"
printf "%-18s %10s (%7s)\n" "Gzipped size:" "$GZIPPED_SIZE bytes" "${GZIPPED_HR}"
