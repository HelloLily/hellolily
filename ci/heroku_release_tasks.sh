#!/bin/bash

# Check if migration is needed.
python manage.py makemigrations --dry-run --noinput | grep -q "No changes detected"

if [ $? -ne 0 ]
then
    echo "Migrations up-to-date with models. Proceed with the deployment"
    exit 0
else
    echo "Migrations needed, setting Heroku app to maintenance mode."
    heroku maintenance:on
    echo "Scaling down beat dynos to 0."
    heroku ps:scale beat=0
    echo "Running migrations."
    python manage.py migrate
    echo "Migrations done, switching maintenance mode off."
    heroku maintenance:off
    echo "Scaling beat dynos up back to 1."
    heroku ps:scale beat=1
fi