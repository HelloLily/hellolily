#!/usr/bin/env bash

set -e

if [ "${TRAVIS_BRANCH}" == "master" ]; then
    # If we're on master check the current commit range.
    if [ $(git log ${TRAVIS_COMMIT_RANGE} --format=oneline -- '**/documents.py' -- ':(exclude)**/email/documents.py' | wc -l) -gt 0 ]; then
        echo "true"
    else
        echo "false"
    fi
elif [ "${TRAVIS_BRANCH}" == "develop" ]; then
    # If we're on develop, compare to master.
    if [ $(git diff --name-only develop..master -- '**/documents.py' -- ':(exclude)**/email/documents.py' | wc -l) -gt 0 ]; then
        echo "true"
    else
        echo "false"
    fi
else
    # On all other branches don't check, just assume yes.
    echo "true"
fi
