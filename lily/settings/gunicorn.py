import os

# Bind to specified ip and port
bind = '%s:%s' % (os.environ.get('IP_ADDRESS', '0.0.0.0'), os.environ.get('PORT', '8000'))

# Use this worker class
worker_class = '%s' % os.environ.get('WORKER_CLASS', 'gevent')

# Use this many workers
workers = int(os.environ.get('WORKERS', 1))

# Each worker has this many threads
threads = int(os.environ.get('THREADS', 100))
