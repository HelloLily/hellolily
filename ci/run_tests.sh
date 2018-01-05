#!/usr/bin/env bash

docker-compose -f docker-compose.yml -f docker-compose.new-build.yml run --rm --service-ports web bash -c "Dockers/wait-for db:5432 && pytest"
