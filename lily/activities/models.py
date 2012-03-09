from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.models import TimeStampedModel
from lily.users.models import UserModel


class ActivityModel(TimeStampedModel):
    """
    Activity model, base class for several activities that users can create for in an activity
    stream.
    """
    
    user = models.ForeignKey(UserModel)
    
    class Meta:
        abstract = True
        verbose_name = _('activity')
        verbose_name_plural = _('activities')


class PollModel(ActivityModel):
    """
    Poll mode, a poll with max. 5 answers.
    """
    
    question = models.TextField(verbose_name=_('question'))
    answer1 = models.CharField(max_length=255, verbose_name=_('option 1'))
    answer2 = models.CharField(max_length=255, verbose_name=_('option 2'))
    answer3 = models.CharField(max_length=255, verbose_name=_('option 3'), blank=True)
    answer4 = models.CharField(max_length=255, verbose_name=_('option 4'), blank=True)
    answer5 = models.CharField(max_length=255, verbose_name=_('option 5'), blank=True)
    
    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = _('poll')
        verbose_name_plural = _('polls')


class BookmarkModel(ActivityModel):
    """
    Bookmark mode, simple url to share an interesting piece of the internet.
    """
    
    url = models.URLField(verbose_name=_('bookmark url'))
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        verbose_name = _('bookmark')
        verbose_name_plural = _('bookmarks')


class EventModel(ActivityModel):
    """
    Event model, a happening with a start/end datetime with optional location/url/description.
    """
    
    title = models.CharField(max_length=150, verbose_name=_('title'))
    date_start = models.DateField(verbose_name=_('start date'))
    time_start = models.TimeField(verbose_name=_('start time'))
    date_end = models.DateField(verbose_name=_('end date'))
    time_end = models.TimeField(verbose_name=_('end time'))
    location = models.CharField(max_length=100, verbose_name=_('location'), blank=True)
    url = models.URLField(verbose_name=_('url'), blank=True)
    description = models.CharField(max_length=255, verbose_name=_('description'), blank=True)

    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')


class StatusModel(ActivityModel):
    """
    Status model, leaving a simple message to leave behind a short update what is going on.
    """
    
    message = models.CharField(max_length=255, verbose_name=_('message'))

    def __unicode__(self):
        return self.message
    
    class Meta:
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
