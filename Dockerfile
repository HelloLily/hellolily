FROM hellolily/baseimage:latest
LABEL maintainer=HelloLily

ENV HOME /home/docker
ARG DOCKER_USER_ID

# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/#/add-or-copy
COPY requirements*.txt $HOME/

RUN pip install -r $HOME/requirements-dev.txt \
    && rm $HOME/requirements.txt $HOME/requirements-dev.txt \
    && addgroup docker && adduser -s /bin/bash -u ${DOCKER_USER_ID:-1000} -D -G docker docker \
    && chown -R docker:docker $HOME/

USER docker

WORKDIR /home/docker/hellolily
