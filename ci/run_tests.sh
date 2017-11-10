#!/usr/bin/env bash

COVERAGE_PROCESS_START=./.coveragerc docker-compose -f docker-compose.yml -f docker-compose.new-build.yml run --rm --service-ports web bash -c "Dockers/wait-for db:5432 && Dockers/wait-for es:9200 && python manage.py search_index create && python manage.py search_index autoalias && coverage run --source='.' --parallel-mode manage.py test --parallel=2"
