from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.models import TimeStampedModel

from lily.users.models import LilyUser


class Activity(TimeStampedModel):
    """
    Activity model, base class for several activities that users can create for in an activity
    stream.
    """
    user = models.ForeignKey(LilyUser)
    
    class Meta:
        abstract = True
        verbose_name = _('activity')
        verbose_name_plural = _('activities')


class Poll(Activity):
    """
    Poll model, a poll with max. 5 answers.
    """
    question = models.TextField(verbose_name=_('question'))
    
    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = _('poll')
        verbose_name_plural = _('polls')


class Choice(models.Model):
    """
    Choice model, simple model with a single charfield to contain one choice for a poll.
    """
    choice = models.CharField(max_length=255, verbose_name=_('choice'))
    poll = models.ForeignKey(Poll, related_name='choices')
    
    class Meta:
        verbose_name = _('choice')
        verbose_name_plural = _('choices')


class Bookmark(Activity):
    """
    Bookmark model, simple url to share an interesting piece of the internet.
    """
    url = models.URLField(max_length=255, verbose_name=_('bookmark url'))
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        verbose_name = _('bookmark')
        verbose_name_plural = _('bookmarks')


class Event(Activity):
    """
    Event model, a happening with date/time fields and optional location/url/description.
    Not all dates are required to e.g. enable one-day events.
    """
    title = models.CharField(max_length=150, verbose_name=_('title'))
    start_date = models.DateField(verbose_name=_('start date'))
    start_time = models.TimeField(verbose_name=_('start time'), blank=True)
    end_date = models.DateField(verbose_name=_('end date'), blank=True)
    end_time = models.TimeField(verbose_name=_('end time'), blank=True)
    location = models.CharField(max_length=100, verbose_name=_('location'), blank=True)
    url = models.URLField(max_length=255, verbose_name=_('url'), blank=True)
    description = models.CharField(max_length=255, verbose_name=_('description'), blank=True)

    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')


class Status(Activity):
    """
    Status model, leaving a simple message behind with a short update what is going on.
    """
    message = models.CharField(max_length=255, verbose_name=_('message'))

    def __unicode__(self):
        return self.message
    
    class Meta:
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
