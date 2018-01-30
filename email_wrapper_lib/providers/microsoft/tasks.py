from celery import shared_task


@shared_task
def do_something():
    print "test"
