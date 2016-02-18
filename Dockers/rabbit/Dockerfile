FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update && \
    apt-get install -y rabbitmq-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 5672

CMD ["/usr/sbin/rabbitmq-server"]
