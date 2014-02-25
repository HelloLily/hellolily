### Django runs on this
web: newrelic-admin run-program python manage.py run_gunicorn 0.0.0.0:$PORT -w 4 -k gevent

### Celery workers

## beat: Trigger tasks for all queues, and processes the ones in queue 'celery'
beat: celery worker -B --app=lily.celery --loglevel=info -Q celery -n beat.%h

## worker: Execute tasks in queue 'queue1'
worker1: celery worker --loglevel=info --app=lily.celery -Q queue1 -n worker1.%h

## worker: Execute tasks in queue 'queue2'
worker2: celery worker --loglevel=info --app=lily.celery -Q queue2 -n worker2.%h --maxtasksperchild=5 --autoscale=4,2

## worker: Execute tasks in queue 'queue3'
worker3: celery worker --loglevel=info --app=lily.celery -Q queue3 -n worker3.%h --maxtasksperchild=5
