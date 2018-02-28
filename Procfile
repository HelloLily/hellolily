## consumer: Run daphne to handle requests and put them in the queue for processing.
web: bin/start-pgbouncer-stunnel newrelic-admin run-program daphne lily.asgi:channel_layer --port $PORT --bind 0.0.0.0

## consumer: Run django channels workers to actually process requests.
consumer: python manage.py runworker

## beat: Trigger tasks for all queues.
beat: REMAP_SIGTERM=SIGQUIT bin/start-pgbouncer-stunnel celery beat --app=lily.celery --loglevel=info

## worker: Execute tasks from all queues.
worker: REMAP_SIGTERM=SIGQUIT bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker --app=lily.celery --loglevel=info --pool=eventlet




## worker: Execute tasks in queue 'email_async_tasks'
#worker1: bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker --loglevel=info --app=lily.celery -Q email_async_tasks -n worker1.%h -c12 -P eventlet --without-gossip --without-mingle --without-heartbeat

## worker: Execute tasks in queue 'email_scheduled_tasks' & 'email_first_sync'
#worker2: bin/start-pgbouncer-stunnel newrelic-admin run-program celery worker --loglevel=info --app=lily.celery -Q email_scheduled_tasks,email_first_sync -n worker2.%h -c12 -P eventlet --without-gossip --without-mingle --without-heartbeat
