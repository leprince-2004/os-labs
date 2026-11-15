#!/bin/bash
# usage: ./ratio.sh a.txt b.txt   - average work per second of each file (without second 1) and ratio a/b
a=$(awk 'NR>1 {s+=$5; n++} END {printf "%.0f", s/n}' "$1")
b=$(awk 'NR>1 {s+=$5; n++} END {printf "%.0f", s/n}' "$2")
echo "$1: $a units/s   $2: $b units/s   ratio a/b = $(awk -v a="$a" -v b="$b" 'BEGIN {printf "%.2f", a/b}')"
