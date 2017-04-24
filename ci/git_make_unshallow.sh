#!/usr/bin/env bash

# Make sure git fetch, gets all the branches, not just the current one.
git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
# Convert this clone into an unshallow one, including all the branches.
git fetch origin --unshallow --quiet

# Set up the master branch if we're not on it.
if [ "${TRAVIS_BRANCH}" != "master" ]; then
    git branch --track "master" "origin/master" --quiet
fi

# Set up the develop branch if we're not on it.
if [ "${TRAVIS_BRANCH}" != "develop" ]; then
    git branch --track "develop" "origin/develop" --quiet
fi

echo "false"
