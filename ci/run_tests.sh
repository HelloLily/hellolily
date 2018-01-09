#!/usr/bin/env bash

COVERAGE_PROCESS_START=./.coveragerc docker-compose -f docker-compose.yml -f docker-compose.new-build.yml run --rm --service-ports web bash -c "Dockers/wait-for db:5432 && coverage run --source='.' --parallel-mode manage.py test --parallel=2"
