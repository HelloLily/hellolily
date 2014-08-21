from celery import states
from django.db import models


STATES_CHOICES = zip(states.ALL_STATES, states.ALL_STATES)


class TaskStatus(models.Model):
    """
    Task status.

    With this the status of celery tasks can be monitored, more reliably than
    depending on the broker or celery itself.
    """
    status = models.CharField(max_length=20, default=states.PENDING, choices=STATES_CHOICES)
    task_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    signature = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True)

    def __unicode__(self):
        return unicode('%s | %s | %s ' % (
            self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            self.status,
            self.signature
        ))

    class Meta:
        app_label = 'taskmonitor'
        verbose_name_plural = 'Task statuses'
