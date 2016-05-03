#!/bin/bash

# Check if there are changes in the models that are not covered by migrations.
# Usefull in a git pre-push hook to prevent incomplete migrations files being pushed.

# -q supresses output from grep.
docker-compose run web python manage.py makemigrations --dry-run --noinput | grep -q "No changes detected"

if [ $? -ne 1 ]
then
    echo "Proceed: migrations up-to-date with models."
    exit 0
else
    echo "Abort: migrations not up-to-date with models."
    exit 1
fi
