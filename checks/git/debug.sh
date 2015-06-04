#!/bin/bash

echo "starting debug statements check."
echo ""

diff="git diff --cached --diff-filter=ACMRTUXB"

# python checks
pdb_count=$($diff | grep ".set_trace()" -c)
echo "$pdb_count pdb statements found"

print_count=$($diff | grep "print" -c)
echo "$print_count print statements found"

# js checks
clog_count=$($diff | grep "console.log" -c)
echo "$print_count console.log statements found"

debugger_count=$($diff | grep "debugger" -c)
echo "$debugger_count debugger statements found"

total=$(($pdb_count+$print_count+$clog_count+$debugger_count))
echo ""
echo "$total debug statements found"
echo ""

exit 0
