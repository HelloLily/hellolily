from datetime import datetime, timedelta

from celery import signature
from celery.states import PENDING, SUCCESS, FAILURE, RECEIVED, STARTED, REVOKED, RETRY, IGNORED, REJECTED
from dateutil.tz import tzutc
from django.conf import settings
from django.db import transaction
from django.db.models import Q

from taskmonitor.models import TaskStatus


def resolve_annotations(task_name):
    annotations_for_task = {}
    annotations = settings.CELERY_ANNOTATIONS
    for annotation, value in annotations.get('*', {}).items():
        annotations_for_task[annotation] = value
    for annotation, value in annotations.get(task_name, {}).items():
        annotations_for_task[annotation] = value
    return annotations_for_task


@transaction.atomic
def lock_task(task_name, *args, **kwargs):
    """
    Try to lock a task: check whether or not a status entry exists for given
    parameters or create one (preventing others from being created).

    Returns whether or not the task was locked and a status instance.
    """
    locked, status = False, None

    # MUST use `str()`, otherwise it will invoke the task instead in the
    # query up ahead!
    sig = str(signature(task_name, args=args, kwargs=kwargs))

    # Create a status if allowed
    if not TaskStatus.objects\
            .filter(Q(expires_at__gte=datetime.now(tzutc())) | Q(expires_at__isnull=True),
                    signature=sig)\
            .filter(status__in=[PENDING, RECEIVED, STARTED, REVOKED, RETRY, IGNORED, REJECTED])\
            .exists():

        # Set status to PENDING since it's not running yet
        init_status = PENDING

        # Check for timelimit
        annotations_for_task = resolve_annotations(task_name)
        timelimit = annotations_for_task.get('time_limit')

        # Determine when this task should expire
        utc_before = datetime.now(tzutc())
        expires_at = utc_before + timedelta(seconds=timelimit)

        status = TaskStatus.objects.create(
            status=init_status,
            signature=sig,
            expires_at=expires_at,
        )
        locked = True

    return locked, status
