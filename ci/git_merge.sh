#!/usr/bin/env bash

can_merge() {
    if [ "${NEXT_ACTION}" == "merge" ]; then
        # Merge when the deploy check indicates we must.
        return 0
    fi

    return 1
}

do_merge() {
    echo "Checking out master."
    git checkout master || exit 1

    echo "Merging develop into master."
    git merge --ff-only --no-edit develop || exit 1
}

if can_merge; then
    echo "Starting merge."
    do_merge
else
    echo "Not merging."
fi
