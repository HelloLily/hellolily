FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update

RUN apt-get install -y \
    python2.7-dev \
    python-pip \
    postgresql \
    postgresql-server-dev-9.3 \
    libxml2-dev \
    libxslt1-dev \
    libncurses5-dev

RUN useradd docker
RUN echo "ALL ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
WORKDIR /home/docker
ENV HOME /home/docker

ADD requirements.txt $HOME/requirements.txt
RUN pip install -r $HOME/requirements.txt

# Workaround for IncompleteRead error while installing requirements-dev.txt.
# See: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991
RUN rm -rf /usr/local/lib/python2.7/dist-packages/requests* && easy_install requests==2.3.0

ADD requirements-dev.txt $HOME/requirements-dev.txt
RUN pip install -r $HOME/requirements-dev.txt
RUN rm $HOME/requirements.txt $HOME/requirements-dev.txt

USER docker

ENV DEBUG 1
ENV SECRET_KEY abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmn
ENV DATABASE_URL postgres://hellolily:@db/hellolily
ENV REDISTOGO_URL=redis://redis:6379
ENV MULTI_TENANT 1
ENV BROKER_HOST rabbit

CMD /bin/bash
