web: python manage.py collectstatic --noinput; newrelic-admin run-program python manage.py run_gunicorn 0.0.0.0:$PORT -w 3 -k gevent
