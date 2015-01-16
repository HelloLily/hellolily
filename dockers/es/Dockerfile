FROM dockerfile/java:oracle-java7
MAINTAINER HelloLily

ENV ES_PKG_NAME elasticsearch-1.3.7

# Install Elasticsearch.
RUN wget https://download.elasticsearch.org/elasticsearch/elasticsearch/$ES_PKG_NAME.tar.gz && \
    tar xvzf $ES_PKG_NAME.tar.gz && \
    rm -f $ES_PKG_NAME.tar.gz && \
    mv $ES_PKG_NAME /elasticsearch

VOLUME ["/elasticsearch/data"]

EXPOSE 9200

CMD ["/elasticsearch/bin/elasticsearch"]
