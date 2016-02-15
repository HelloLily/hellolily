import os

# Turn 0 or 1 into False/True respectively.
from Crypto import Random


# Turn 0 or 1 into False/True respectively.
def boolean(value):
    return bool(int(value))


# By preloading an application you can save some RAM resources as well as speed up server boot times.
# Although, if you defer application loading to each worker process, you can reload your application
# code easily by restarting workers.
preload_app = boolean(os.environ.get('WEB_PRELOAD_APP', 0))

# Bind to specified ip and port.
bind = '%s:%s' % (os.environ.get('IP_ADDRESS', '0.0.0.0'), os.environ.get('PORT', '8000'))

# Use this worker class
worker_class = '%s' % os.environ.get('WORKER_CLASS', 'gevent')

# Use this many workers, web_concurrency is a best practice name, value is automatically calculated by Heroku.
workers = int(os.environ.get('WEB_CONCURRENCY', 2))

# Each worker has this many threads.
threads = int(os.environ.get('WEB_CONCURRENCY_THREADS', 10))

secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

forwarded_allow_ips = '*'


#
# Server hooks
#
def post_fork(server, worker):
    """
    Called just after a worker has been forked.

    A callable that takes a server and worker instance as arguments.
    """
    # Random needs to know when it's being run inside a fork, otherwise it throws exceptions.
    Random.atfork()
