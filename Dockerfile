FROM jfloff/alpine-python:2.7
MAINTAINER HelloLily

# Add docker user and group first to make sure their IDs get assigned consistently,
# regardless of whatever dependencies get added
RUN addgroup docker && adduser -s /bin/bash -D -G docker docker
ENV HOME /home/docker
WORKDIR /home/docker

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
COPY requirements.txt $HOME/requirements.txt
COPY requirements-dev.txt $HOME/requirements-dev.txt

# Also installs the normal requirements file.
RUN pip install -r $HOME/requirements-dev.txt
RUN rm $HOME/requirements.txt $HOME/requirements-dev.txt

# Switch to docker user.
RUN chown -R docker:docker $HOME/
USER docker

WORKDIR /home/docker/hellolily
