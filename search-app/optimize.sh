#!/bin/sh

set -e

js=$2
min=$3

elm-optimize-level-2 --optimize-speed --output=$js $1
swc $js -o $min

echo "Initial size: $(cat $js | wc -c) bytes  ($js)"
echo "Minified size:$(cat $min | wc -c) bytes  ($min)"
echo "Gzipped size: $(cat $min | gzip -c | wc -c) bytes"
