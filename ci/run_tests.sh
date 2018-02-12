#!/usr/bin/env bash

command="echo \"Waiting for DB...\" \
 && Dockers/wait-for db:5432 \
 && echo \"DB is up!\" \
 && echo \"Waiting for ES...\" \
 && Dockers/wait-for es:9200 \
 && echo \"ES is up!\" \
 && python manage.py search_index create \
 && python manage.py search_index autoalias \
 && coverage run --source='.' --parallel-mode manage.py test --parallel=2"

docker-compose -f docker-compose.yml -f docker-compose.new-build.yml run --rm --service-ports web bash -c "${command}"
