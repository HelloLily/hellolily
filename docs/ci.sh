#!/bin/bash -x

set -e

COMPOSE_FILE=docker-compose.yml

# Run CI tests, start by printing a warning.
echo "Warning, this script removes the lily/static/ dir and docker containers/volumes, hit CTRL+C in 5 secs to abort."
sleep 5

# Remove possible previous state.
sudo docker-compose -f $COMPOSE_FILE kill
sudo docker-compose -f $COMPOSE_FILE rm -vf
sudo docker-compose -f $COMPOSE_FILE build
rm lily/static/ -rf

# Initialize setup.
sudo docker run --rm -v $(pwd):/home/docker ferdynice/gulpy npm install
sudo docker run --rm -v $(pwd):/home/docker ferdynice/gulpy gulp build

# Wait for db service to be fully initialized.
sudo docker-compose run --rm web ls
sleep 5

# Run the tests.
set +e
RESULT=0
if [ $? -ne 0 ]; then RESULT+=1; fi
sudo docker-compose -f $COMPOSE_FILE run --rm --service-ports web python manage.py test -v2 \
    --with-coverage --cover-package=lily --cover-xml --cover-xml-file=coverage.xml \
    --with-xunit --xunit-file=TESTS-django.xml
EC=$?
if [ $EC -ne 0 ]; then RESULT+=1; fi

# Sphinx docs.
sudo docker-compose -f $COMPOSE_FILE run --rm web make -C docs/sphinx allhtml

# Cleanup.
sudo docker-compose -f $COMPOSE_FILE kill
sudo docker-compose -f $COMPOSE_FILE rm -vf

exit $RESULT
