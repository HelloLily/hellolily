FROM postgres:9.3
MAINTAINER HelloLily

ADD init_lily.sh /docker-entrypoint-initdb.d/
ADD create_db_with_user.sql /docker-entrypoint-initdb.d/
