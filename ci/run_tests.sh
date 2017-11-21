#!/usr/bin/env bash

docker-compose -f docker-compose.yml -f docker-compose.new-build.yml run --rm --service-ports web bash -c "sleep 15 && python manage.py test --with-coverage --cover-erase --cover-package=lily"
