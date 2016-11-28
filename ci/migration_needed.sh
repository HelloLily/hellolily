#!/usr/bin/env bash

set -e

if [ $(git log ${TRAVIS_COMMIT_RANGE} --format=oneline -- '**/migrations/*' | wc -l) -gt 0 ]; then
    echo "true"
else
    echo "false"
fi
