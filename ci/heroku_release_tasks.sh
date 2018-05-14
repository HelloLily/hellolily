#!/bin/bash

# Run migrations if needed.
if [ $(python manage.py showmigrations | grep '\[ \]' | wc -l) -gt 0 ]; then
    echo "Migrations needed, setting Heroku app to maintenance mode."
    python ./ci/patch_heroku_app.py ${HEROKU_APP_NAME} ${HEROKU_API_KEY} maintenance true
    echo "Scaling down beat dynos to 0."
    python ./ci/patch_heroku_app.py ${HEROKU_APP_NAME}/formation/beat ${HEROKU_API_KEY} quantity 0
    echo "Running migrations."
    python manage.py migrate
    echo "Migrations done, switching maintenance mode off."
    python ./ci/patch_heroku_app.py ${HEROKU_APP_NAME} ${HEROKU_API_KEY} maintenance false
    echo "Scaling beat dynos up back to 1."
    python ./ci/patch_heroku_app.py ${HEROKU_APP_NAME}/formation/beat ${HEROKU_API_KEY} quantity 1
else
    echo "No Migration needed, proceeding with the deployment."
fi