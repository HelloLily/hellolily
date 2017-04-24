#!/usr/bin/env bash

can_merge() {
    if [ "${NEXT_ACTION}" == "merge" ]; then
        # Merge when the deploy check indicates we must.
        return 0
    fi

    return 1
}

do_push() {
    echo "Pushing to ${GITHUB_REPO}"
    # Redirect to /dev/null to avoid secret leakage.
    git push "${GITHUB_URI}" master >/dev/null 2>&1
}

if can_merge; then
    echo "Starting push."
    do_push
else
    echo "Not pushing."
fi
