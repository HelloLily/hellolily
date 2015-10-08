FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update && apt-get install -y \
    python2.7-dev \
    python-pip \
    postgresql \
    postgresql-server-dev-9.3 \
    libxml2-dev \
    libxslt1-dev \
    libncurses5-dev \
    rsync \
    nodejs \
    npm

RUN useradd docker
RUN echo "ALL ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
WORKDIR /home/docker
ENV HOME /home/docker

# For our e2e tests we need protractor
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g protractor

ADD requirements.txt $HOME/requirements.txt
RUN pip install -r $HOME/requirements.txt

# Workaround for IncompleteRead error while installing requirements-dev.txt.
# See: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991
RUN rm -rf /usr/local/lib/python2.7/dist-packages/requests* && easy_install requests==2.3.0

ADD requirements-dev.txt $HOME/requirements-dev.txt
RUN pip install -r $HOME/requirements-dev.txt
RUN rm $HOME/requirements.txt $HOME/requirements-dev.txt

# Switch to docker user.
RUN chown -R docker:docker $HOME/
USER docker

# Workaround for IncompleteRead error while installing PuDB.
# See: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991
RUN sudo rm -rf /usr/local/lib/python2.7/dist-packages/requests* && sudo easy_install requests==2.3.0

# Install PuDB.
# PuDB does some weird folder creating stuff, leaving it unable to read with no apparent reason.
RUN mkdir -p $HOME/.config/pudb
RUN sudo pip install pudb
RUN sudo chown -R docker:docker $HOME/

# Workaround for https://github.com/angular/protractor/issues/2588
RUN sudo npm install -g protractor@2.2.0

ENV DEBUG 1
ENV SECRET_KEY abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmn
ENV DATABASE_URL postgres://hellolily:@db/hellolily
ENV REDISTOGO_URL redis://redis:6379
ENV MULTI_TENANT 1
ENV BROKER_HOST rabbit
ENV SEARCHBOX_SSL_URL http://es:9200

WORKDIR /home/docker/hellolily
