#!/bin/bash

FLAKE_WITH_PARAMS="flake8 --max-line-length=119 --format='%(path)s %(row)d:%(col)d [%(code)s] %(text)s'"

echo "Starting flake check"
echo ""

# PEP check, are you making it worse?
total=0
git diff --cached --name-status |
sed -e 's/^[^[:blank:]]*[[:blank:]]*//;/\.py$/!d;/\/migrations\//d' |
while read file; do
    temp="${file}.py"
    test -f "$temp" && echo "$temp: precheck: Temp file exists, please rm it" 2>&1 && exit 1
    mkdir -p "`dirname "$temp"`"  # if files are new/moved we may need the directory
    git show "HEAD:$file" >"$temp" 2>/dev/null  # empty files, no problem
    before=`eval $FLAKE_WITH_PARAMS "$temp" | wc -l`
    if ! git diff --cached "$file" 2>/dev/null | patch --forward --quiet "$temp"; then  # patch staged only
        cp "$file" "$temp"
    fi
    after=`eval $FLAKE_WITH_PARAMS "$temp" | wc -l`
    rm "$temp"
    if test $after -gt $before; then
        echo "$file: pepcheck: Making it worse ($before to $after)" >&2
        total=$((total+1))
    fi
    rmdir -p "`dirname "$temp"`" 2> /dev/null  # clean up any dirs we made
    test $total -eq 0  # propagate failure status to outside the while
done
