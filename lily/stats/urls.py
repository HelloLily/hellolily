from django.conf.urls import patterns, url

from .views import (CasesTotalCountLastWeek, CasesPerTypeCountLastWeek, CasesWithTagsLastWeek, CasesCountPerStatus,
                    CasesTopTags, DealsUnsentFeedbackForms, DealsUrgentFollowUp, DealsWon, DealsLost, DealsAmountRecurring)

urlpatterns = patterns(
    '',
    url(r'^cases/total/(?P<lilygroup_id>[\d]+)/$', CasesTotalCountLastWeek.as_view()),
    url(r'^cases/grouped/(?P<lilygroup_id>[\d]+)/$', CasesPerTypeCountLastWeek.as_view()),
    url(r'^cases/withtags/(?P<lilygroup_id>[\d]+)/$', CasesWithTagsLastWeek.as_view()),
    url(r'^cases/countperstatus/(?P<lilygroup_id>[\d]+)/$', CasesCountPerStatus.as_view()),
    url(r'^cases/toptags/(?P<lilygroup_id>[\d]+)/$', CasesTopTags.as_view()),

    url(r'^deals/unsentfeedback/$', DealsUnsentFeedbackForms.as_view()),
    url(r'^deals/urgentfollowup/$', DealsUrgentFollowUp.as_view()),
    url(r'^deals/won/$', DealsWon.as_view()),
    url(r'^deals/lost/$', DealsLost.as_view()),
    url(r'^deals/amountrecurring/$', DealsAmountRecurring.as_view()),
)
