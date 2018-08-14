from django.conf.urls import url

from .views import (
    CasesTotalCountLastWeek, CasesPerTypeCountLastWeek, CasesWithTagsLastWeek, CasesCountPerStatus, CasesTopTags,
    DealsUrgentFollowUp, DealsWon, DealsLost, DealsAmountRecurring
)

case_patterns = [
    url(r'^cases/total/(?P<team_id>[\d]+)/$', CasesTotalCountLastWeek.as_view(), name='stats_cases_total'),
    url(r'^cases/grouped/(?P<team_id>[\d]+)/$', CasesPerTypeCountLastWeek.as_view(), name='stats_cases_grouped'),
    url(r'^cases/withtags/(?P<team_id>[\d]+)/$', CasesWithTagsLastWeek.as_view(), name='stats_cases_withtags'),
    url(r'^cases/countperstatus/(?P<team_id>[\d]+)/$', CasesCountPerStatus.as_view(), name='stats_cases_cps'),
    url(r'^cases/toptags/(?P<team_id>[\d]+)/$', CasesTopTags.as_view(), name='stats_cases_toptags'),
]

deal_patterns = [
    url(r'^deals/urgentfollowup/$', DealsUrgentFollowUp.as_view(), name='stats_deals_urgent_followup'),
    url(r'^deals/won/$', DealsWon.as_view(), name='stats_deals_won'),
    url(r'^deals/lost/$', DealsLost.as_view(), name='stats_deals_lost'),
    url(r'^deals/amountrecurring/$', DealsAmountRecurring.as_view(), name='stats_deals_amount_recurring'),
]

urlpatterns = case_patterns + deal_patterns
