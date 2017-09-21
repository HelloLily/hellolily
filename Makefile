# Makefile for Lily development
# Tabs for MacOS compatibility

default: run

build:
	@echo "Make: DOCKER_USER_ID=1000 docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build"
	@echo ""
	@DOCKER_USER_ID=1000 docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build
	@echo ""
	@echo "Make: gulp clean"
	@echo ""
	@gulp clean
	@echo ""
	@echo "Make: NODE_ENV=dev gulp build"
	@echo ""
	@NODE_ENV=dev gulp build
	@echo ""

pull:
	@echo "Make: docker-compose pull"
	@echo ""
	@docker-compose pull
	@echo ""

makemigrations:
	@echo "Make: docker-compose run --rm web python manage.py makemigrations"
	@echo ""
	@docker-compose run --rm web python manage.py makemigrations
	@echo ""

migrate:
	@echo "Make: docker-compose run --rm web python manage.py migrate"
	@echo ""
	@docker-compose run --rm web python manage.py migrate
	@echo ""

index:
	@echo "Make: docker-compose run --rm web python manage.py index -f"
	@echo ""
	@docker-compose run --rm web python manage.py index -f
	@echo ""

test:
	@echo "Make: docker-compose run --rm -e ES_DISABLED=1 --service-ports web python manage.py test"
	@echo ""
	@docker-compose run --rm --service-ports -e ES_DISABLED=1 web python manage.py test
	@echo ""

testdata:
	@echo "Make: docker-compose run --rm web python manage.py testdata"
	@echo ""
	@docker-compose run --rm web python manage.py testdata
	@echo ""

run:
	@echo "Make: docker-compose run --rm --service-ports web & gulp watch"
	@echo ""
	@docker-compose run --rm --service-ports web & gulp watch
	@echo ""

up:
	@echo "Make: docker-compose up & gulp watch"
	@echo ""
	@docker-compose up & gulp watch
	@echo ""

down:
	@echo "Make: docker-compose down"
	@echo ""
	@docker-compose down
	@echo ""

manage:
	@echo "Make: docker-compose run --rm web python manage.py ${cmd}"
	@echo ""
	@docker-compose run --rm web python manage.py ${cmd}
	@echo ""

setup: build migrate index testdata run

help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

.PHONY: default build pull makemigrations migrate index testdata run up down manage setup help
