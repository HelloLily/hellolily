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

RUN mkdir /home/docker
RUN chown -R root /home/docker
ENV HOME /home/docker
WORKDIR /home/docker

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#/add-or-copy
COPY requirements.txt $HOME/requirements.txt
COPY requirements-dev.txt $HOME/requirements-dev.txt

# Also installs the normal requirements file.
RUN pip install -r $HOME/requirements-dev.txt

RUN rm $HOME/requirements.txt $HOME/requirements-dev.txt

WORKDIR /home/docker/hellolily
