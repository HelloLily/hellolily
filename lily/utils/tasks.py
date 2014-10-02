import logging

from celery.task import task
from django.core.management import call_command

task_logger = logging.getLogger('celery_task')

@task(name='import_sugar_csv')
def import_sugar_csv(model, path, tenant):
    task_logger.info('importing from sugar file started')
    call_command('sugarcsvimport', model, path, tenant, verbosity=0)
