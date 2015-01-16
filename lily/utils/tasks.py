import logging

from celery.task import task
from django.core.management import call_command


logger = logging.getLogger(__name__)


@task(name='import_sugar_csv')
def import_sugar_csv(model, path, tenant, sugar_import):
    if sugar_import:
        logger.info('importing from sugar file started')
    else:
        logger.info('importing from other file started')
    call_command('sugarcsvimport', model, path, tenant, sugar_import, verbosity=0)
