import logging

from celery.task import task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@task(name='import_sugar_csv')
def import_sugar_csv(model, path, tenant, sugar_import):
    if model == 'function':
        call_command('sugarcsvimport_function', path, tenant, verbosity=0)
    else:
        if sugar_import:
            logger.info('importing from sugar file started')
        else:
            logger.info('importing from other file started')
        call_command('sugarcsvimport', model, path, tenant, sugar_import, verbosity=0)


@task(name='clear_sessions_scheduler')
def clear_sessions_scheduler():
    """
    Call the Django provided management command to clear expired sessions.
    """
    call_command('clearsessions', interactive=False)
