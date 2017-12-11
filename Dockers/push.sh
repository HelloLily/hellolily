#!/usr/bin/env bash

if [ "${TRAVIS_BRANCH}" != "master" ]; then
    echo "Not pushing because we're on the wrong branch."
elif [ "${TRAVIS_EVENT_TYPE}" != "push" ]; then
    echo "Not pushing because the build is not triggered by the git hook."
else
    echo "Branch is master and build is triggered by the git hook, starting push."

    docker login -u="${DOCKER_HUB_USERNAME}" -p="${DOCKER_HUB_PASSWORD}"
    docker push hellolily/hellolily-app:latest
fi
