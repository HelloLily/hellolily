FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update

RUN apt-get install -y \
    rabbitmq-server

RUN rabbitmq-plugins enable rabbitmq_management

EXPOSE 5672

CMD ["/usr/sbin/rabbitmq-server"]
