# Makefile for Lily development
# Tabs for MacOS compatibility

default: run

build:
	@echo "Make: docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build"
	@echo ""
	@docker-compose -f docker-compose.yml -f docker-compose.new-build.yml build
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
	@echo "Make: docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py migrate'"
	@echo ""
	@docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py migrate'
	@echo ""

index:
	@echo "Make: docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && Dockers/wait-for es:9200 && python manage.py search_index rebuild -f'"
	@echo ""
	@docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && Dockers/wait-for es:9200 && python manage.py search_index rebuild -f'
	@echo ""

test:
	@echo "Make: docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py test'"
	@echo ""
	@docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py test'
	@echo ""

testdata:
	@echo "Make: docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py testdata'"
	@echo ""
	@docker-compose run --rm web bash -c 'Dockers/wait-for db:5432 && python manage.py testdata'
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

cleanfiles:
	@echo "Make: rm -rf lily/files/"
	@echo ""
	@rm -rf lily/files/
	@echo ""

setup: pull build migrate testdata index run

help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

.PHONY: default build pull makemigrations migrate index testdata run up down manage cleanfiles setup help
