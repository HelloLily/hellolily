#!/usr/bin/env python
import os
from subprocess import check_output
import sys
from urlparse import urlparse


DEFAULT_APP = 'hellolily'


def connect(app):
    database_url = check_output(['heroku', 'config:get', 'DATABASE_URL', '--app', app])
    urlparts = urlparse(database_url)
    cmd = 'psql -h %s -d %s -p %s -U %s' % (
        urlparts.hostname,
        urlparts.path.lstrip('/').rstrip(),
        urlparts.port,
        urlparts.username,
    )
    os.environ['PGPASSWORD'] = urlparts.password
    os.system(cmd)


if __name__ == '__main__':
    app = DEFAULT_APP
    if len(sys.argv[1:]) == 1:
        app = sys.argv[1]
    connect(app)
