### Django runs on this
web: bin/start-pgbouncer daphne lily.asgi:channel_layer --port $PORT --bind 0.0.0.0 --http-timeout 28

consumer: python manage.py runworker

### Celery workers

## beat: Trigger tasks for all queues, and processes the ones in queue 'celery'
beat: bin/start-pgbouncer celery worker -B --app=lily.celery --loglevel=info -Q celery -n beat.%h

## worker: Execute tasks in queue 'email_async_tasks'
worker1: bin/start-pgbouncer celery worker --loglevel=info --app=lily.celery -Q email_async_tasks -n worker1.%h -c12 -P eventlet --without-gossip --without-mingle --without-heartbeat

## worker: Execute tasks in queue 'email_scheduled_tasks' & 'email_first_sync'
worker2: bin/start-pgbouncer celery worker --loglevel=info --app=lily.celery -Q email_scheduled_tasks,email_first_sync,other_tasks -n worker2.%h -c12 -P eventlet --without-gossip --without-mingle --without-heartbeat
