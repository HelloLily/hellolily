FROM postgres:9.5
MAINTAINER HelloLily

ADD init.sh /docker-entrypoint-initdb.d/
ADD create_db_with_user.sql /docker-entrypoint-initdb.d/
