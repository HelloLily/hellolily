#!/usr/bin/env bash

if [ "${TRAVIS_EVENT_TYPE}" == "cron" ]; then
    # Assume we are on the develop branch, because that's the only one with a cron job.
    echo 'merge'
elif [ "${TRAVIS_BRANCH}" == "develop" ] && [ "${TRAVIS_EVENT_TYPE}" == "push" ]; then
    if [ "${MIGRATION_NEEDED}" == "false" ] && [ "${ES1_INDEXING_NEEDED}" == "false" ] && [ "${ES6_INDEXING_NEEDED}" == "false" ]; then
        # Migration/index is not needed.
        echo 'merge'
    else
        # Only merge develop into master with migrations/index needed when the cronjob runs.
        echo 'false'
    fi
elif [ "${TRAVIS_BRANCH}" == "master" ] && [ "${TRAVIS_EVENT_TYPE}" == "push" ]; then
    # Once a commit hits master, assume it's important and deploy immediately.
    echo 'deploy'
else
    echo 'false'
fi
