#!/bin/bash

empty_translations=$(grep -r '""' locale -c)
empty_translations_count=0

for line in $empty_translations
do
    count=$(cut -d ':' -f2 <<< $line)
    empty_translations_count=$((empty_translations_count+count))

    echo "empty: $line"
done

fuzzy_translations=$(grep -r 'fuzzy' locale -c)
fuzzy_translations_count=0

for line in $fuzzy_translations
do
    count=$(cut -d ':' -f2 <<< $line)
    fuzzy_translations_count=$((fuzzy_translations_count+count))

    echo "fuzzy: $line"
done

total=$(($empty_translations_count+fuzzy_translations_count))

exit $total
