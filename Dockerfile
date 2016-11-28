FROM jfloff/alpine-python:2.7
MAINTAINER HelloLily

RUN apk add --update \
    linux-headers \
    postgresql-dev=9.5.4-r0 \
    libxml2-dev \
    libxslt-dev \
    ncurses5-libs \
    rsync \
    nodejs \
    libjpeg-turbo-dev

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#/add-or-copy
COPY requirements.txt requirements.txt
COPY requirements-dev.txt requirements-dev.txt
RUN pip install -r requirements-dev.txt
RUN rm requirements.txt requirements-dev.txt

RUN addgroup docker && adduser -s /bin/bash -D -G docker docker
ENV HOME /home/docker
RUN chown -R docker:docker $HOME/
USER docker

WORKDIR /home/docker/hellolily
