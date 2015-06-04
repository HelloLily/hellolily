FROM ubuntu:14.04
MAINTAINER HelloLily

RUN apt-get update && \
    apt-get install -y \
    nodejs \
    npm

RUN useradd docker
RUN echo "ALL ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers
WORKDIR /home/docker
ENV HOME /home/docker

RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install -g gulp

# Switch to docker user.
RUN chown -R docker:docker $HOME/
USER docker

ADD package.json $HOME/package.json
RUN npm install

CMD gulp watch
