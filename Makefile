# Makefile for Lily development
# Tabs for MacOS compatibility

default: run

build:
	@docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build
	@gulp clean
	@NODE_ENV=dev gulp build

pull:
	@docker-compose pull

migrate:
	@docker-compose run --rm web python manage.py migrate

index:
	@docker-compose run --rm web python manage.py index -f

testdata:
	@docker-compose run --rm web python manage.py testdata

run:
	@docker-compose run --rm --service-ports web & gulp watch

up:
	@docker-compose up & gulp watch

down:
	@docker-compose down

setup: build migrate index testdata run

help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

.PHONY: default build pull migrate index testdata run up down setup help
