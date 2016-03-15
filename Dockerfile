FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
      python2.7-dev \
      python-pip \
      postgresql \
      postgresql-server-dev-9.3 \
      libxml2-dev \
      libxslt1-dev \
      libncurses5-dev \
      rsync \
      nodejs \
      npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# For our e2e tests we need protractor
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g protractor

# Workaround for IncompleteRead error while installing requirements-dev.txt.
# See: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991
RUN rm -rf /usr/local/lib/python2.7/dist-packages/requests* && easy_install requests==2.3.0

# Install PuDB.
# PuDB does some weird folder creating stuff, leaving it unable to read with no apparent reason.
RUN mkdir -p /root/.config/pudb && pip install pudb

WORKDIR /root/
ADD . /root/

# Workaround for https://github.com/angular/protractor/issues/2588
RUN npm install -g protractor@2.2.0 && npm install

# Install and run gulp
RUN npm install --global gulp-cli && gulp build

# Install pip dependencies
RUN pip install -r requirements-dev.txt

# Workaround for IncompleteRead error while installing PuDB.
# See: https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1306991
RUN rm -rf /usr/local/lib/python2.7/dist-packages/requests* && easy_install requests==2.3.0

# Expose to Selenium.
EXPOSE 8081

ENV DEBUG 1
ENV SECRET_KEY abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmn
ENV DATABASE_URL postgres://hellolily:@db/hellolily
ENV MULTI_TENANT 1

CMD python manage.py runserver 0:8000
