FROM ubuntu:14.04
MAINTAINER HelloLily

ENV ES_PKG_NAME elasticsearch-1.7.2

# Install Java
RUN apt-get update && \
    apt-get install -y openjdk-7-jdk wget && \
    export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64 && \
    wget https://download.elasticsearch.org/elasticsearch/elasticsearch/$ES_PKG_NAME.tar.gz && \
    tar xvzf $ES_PKG_NAME.tar.gz && \
    rm -f $ES_PKG_NAME.tar.gz && \
    mv $ES_PKG_NAME /elasticsearch && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

VOLUME ["/elasticsearch/data"]

EXPOSE 9200

CMD ["/elasticsearch/bin/elasticsearch"]
