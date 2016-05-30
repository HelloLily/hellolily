from django.conf.urls import patterns, url

from .views import (CasesTotalCountLastWeek, CasesPerTypeCountLastWeek, CasesWithTagsLastWeek, CasesCountPerStatus,
                    CasesTopTags, DealsUnsentFeedbackForms, DealsUrgentFollowUp, DealsWon, DealsLost,
                    DealsAmountRecurring)

case_patterns = patterns(
    '',
    url(r'^cases/total/(?P<lilygroup_id>[\d]+)/$', CasesTotalCountLastWeek.as_view(), name='stats_cases_total'),
    url(r'^cases/grouped/(?P<lilygroup_id>[\d]+)/$', CasesPerTypeCountLastWeek.as_view(), name='stats_cases_grouped'),
    url(r'^cases/withtags/(?P<lilygroup_id>[\d]+)/$', CasesWithTagsLastWeek.as_view(), name='stats_cases_withtags'),
    url(r'^cases/countperstatus/(?P<lilygroup_id>[\d]+)/$', CasesCountPerStatus.as_view(), name='stats_cases_cps'),
    url(r'^cases/toptags/(?P<lilygroup_id>[\d]+)/$', CasesTopTags.as_view(), name='stats_cases_toptags'),
)

deal_patterns = patterns(
    '',
    url(r'^deals/unsentfeedback/$', DealsUnsentFeedbackForms.as_view(), name='stats_deals_unsent_feedback'),
    url(r'^deals/urgentfollowup/$', DealsUrgentFollowUp.as_view(), name='stats_deals_urgent_followup'),
    url(r'^deals/won/$', DealsWon.as_view(), name='stats_deals_won'),
    url(r'^deals/lost/$', DealsLost.as_view(), name='stats_deals_lost'),
    url(r'^deals/amountrecurring/$', DealsAmountRecurring.as_view(), name='stats_deals_amount_recurring'),
)


urlpatterns = case_patterns + deal_patterns
