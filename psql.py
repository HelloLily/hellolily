#!/usr/bin/env python
import os
from subprocess import check_output
from urlparse import urlparse


def connect():
    database_url = check_output(['heroku', 'config:get', 'DATABASE_URL'])
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
    connect()
