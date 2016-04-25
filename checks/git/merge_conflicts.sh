#!/bin/bash

echo "Starting merge conflicts markers check."
echo ""

diff="git diff --cached --diff-filter=ACMRTUXB"

# Checking on leftovers of merge conflicts.
marker1_count=$($diff | grep "<<<<<<<" -c)
echo "$marker1_count <<<<<<< marker found."

marker2_count=$($diff | grep "=======" -c)
echo "$marker2_count ======= marker found."

marker3_count=$($diff | grep ">>>>>>>" -c)
echo "$marker3_count >>>>>>> marker found."

total=$(($marker1_count+$marker2_count+$marker3_count))
echo ""
echo "$total merge conflict markers found."
echo ""

exit 0
