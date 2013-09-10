web: newrelic-admin run-program python manage.py run_gunicorn 0.0.0.0:$PORT -w 3 -k gevent
celeryd: python manage.py celeryd --events --beat --loglevel=INFO --concurrency=3 --autoreload
worker: python manage.py celerycam