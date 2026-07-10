#!/bin/sh

set -e

js=$2
min=$3

lamdera make --no-wire --optimize --output="$js" "$1"
INITIAL_SIZE=$(wc -c < "$js")

swc "$js" --out-file "$min"

MINIFIED_SIZE=$(wc -c < "$min")
GZIPPED_SIZE=$(gzip -c "$min" | wc -c)

human_size() {
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec-i --suffix=B "$1"
  else
    printf "%sB" "$1"
  fi
}

# Convert to human-readable format
INITIAL_HR=$(human_size "$INITIAL_SIZE")
MINIFIED_HR=$(human_size "$MINIFIED_SIZE")
GZIPPED_HR=$(human_size "$GZIPPED_SIZE")

# Display results with alignment
printf "%-18s %10s (%7s)  %s\n" "Initial size:" "$INITIAL_SIZE bytes" "${INITIAL_HR}" "$js"
printf "%-18s %10s (%7s)  %s\n" "Minified size:" "$MINIFIED_SIZE bytes" "${MINIFIED_HR}" "$min"
printf "%-18s %10s (%7s)\n" "Gzipped size:" "$GZIPPED_SIZE bytes" "${GZIPPED_HR}"
