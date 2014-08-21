import functools
from datetime import datetime, timedelta

from celery.states import STARTED, SUCCESS, FAILURE
from dateutil.tz import tzutc

from taskmonitor.models import TaskStatus


def monitor_task(method=None, logger=None):
    """
    Decorator which monitors the task status.
    """
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if method is None:
        return functools.partial(monitor_task, logger=logger)

    @functools.wraps(method)
    def f(self, *args, **kwargs):
        task_status = TaskStatus.objects.get(id=kwargs.pop('status_id'))
        task_status.task_id = self.request.id

        # Update expires_at
        utc_before = datetime.now(tzutc())
        expires_at = utc_before + timedelta(seconds=self.request.timelimit[0])
        task_status.expires_at = expires_at

        # Run the task
        task_status.status = STARTED
        task_status.save()

        result = None
        end_status = SUCCESS
        try:
            result = method(*args, **kwargs)
        except Exception, e:  # pylint: disable=W0703
            if logger:
                logger.warning(e)
            end_status = FAILURE
        else:
            # Update status afterwards
            utc_after = datetime.now(tzutc())
            if task_status.expires_at and utc_after > task_status.expires_at:
                end_status = FAILURE

        task_status.status = end_status
        task_status.save()

        return result
    return f
