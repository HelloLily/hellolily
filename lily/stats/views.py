import anyjson
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.http import HttpResponse
from django.views.generic import View

from lily.deals.models import DealStatus


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict
    """
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]


class RawDatabaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        query = self.get_query(request, *args, **kwargs)

        if query:
            cursor = connection.cursor()
            cursor.execute(query)

            results = self.parse_results(dictfetchall(cursor))
        else:
            results = []

        return HttpResponse(anyjson.dumps(results))

    def get_query(self, request, *args, **kwargs):
        raise NotImplementedError

    def parse_results(self, results):
        parsed_results = []
        for row in results:
            parsed_row = {}
            for key, value in row.iteritems():
                try:
                    parsed_row[key] = str(value)
                except UnicodeEncodeError:
                    parsed_row[key] = unicode(value, 'utf-8', errors='ignore')
            parsed_results.append(parsed_row)
        return parsed_results


class CasesTotalCountLastWeek(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count (cases_case.id)
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_teams
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_teams.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_teams.team_id = {team_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN  date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second';
        '''.format(
            tenant_id=request.user.tenant_id,
            team_id=int(kwargs['team_id']),
        )


class CasesPerTypeCountLastWeek(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count(cases_case.id),
                cases_casetype.name,
                date_trunc( 'week', now() - interval '1 week' ) as from,
                (date_trunc('week', now() - interval '1 week' ) + interval '1 week' - interval '1 second') as to,
                EXTRACT(WEEK FROM date_trunc( 'week', now() - interval '1 week' )) as weeknr
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_teams
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_teams.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_teams.team_id = {team_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN  date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second'
            GROUP BY
                cases_casetype.name;
        '''.format(
            tenant_id=request.user.tenant_id,
            team_id=int(kwargs['team_id']),
        )


class CasesWithTagsLastWeek(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count(DISTINCT(cases_case.id)),
                date_trunc( 'week', now() - interval '1 week' ) as start,
                (date_trunc( 'week', now() - interval '1 week' ) + interval '1 week' - interval '1 second') as end
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_teams,
                tags_tag
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_teams.case_id AND
                cases_case.id = tags_tag.object_id AND
                tags_tag.name != '' AND
                tags_tag.tenant_id = {tenant_id} AND
                cases_case_assigned_to_teams.team_id = {team_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second';
        '''.format(
            tenant_id=request.user.tenant_id,
            team_id=int(kwargs['team_id']),
        )


class CasesCountPerStatus(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count (cases_case.id), cases_casestatus.name
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_teams
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_teams.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_teams.team_id = {team_id} AND
                cases_case.is_deleted = false AND
                cases_case.is_archived = false AND
                cases_casestatus.name != 'Closed'
            GROUP BY
                cases_casestatus.name;
          '''.format(
            tenant_id=request.user.tenant_id,
            team_id=int(kwargs['team_id']),
        )


class CasesTopTags(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count(tags_tag.name), tags_tag.name
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_teams,
                tags_tag
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_teams.case_id AND
                cases_case.id = tags_tag.object_id AND
                tags_tag.name <> '' AND
                tags_tag.tenant_id = {tenant_id} AND
                cases_case.is_deleted = false AND
                cases_case.created BETWEEN date_trunc('month', now()- interval '1 month') AND
                date_trunc('month', now()) - interval '1 second' AND
                cases_case_assigned_to_teams.team_id = {team_id} AND
                cases_casetype.name != 'Config' AND
                cases_casetype.name != 'Retour' AND
                cases_casetype.name != 'Callback'
            GROUP BY
                tags_tag.name
            HAVING
                COUNT (tags_tag.name) > 2
            ORDER BY
                count(tags_tag.name) desc
            LIMIT 15;
          '''.format(
            tenant_id=request.user.tenant_id,
            team_id=int(kwargs['team_id']),
        )


class DealsUrgentFollowUp(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        try:
            deal_status_open = DealStatus.objects.get(name='Open')
            deal_status_proposal_sent = DealStatus.objects.get(name='Proposal sent')
        except DealStatus.DoesNotExist:
            return ''

        return '''
            SELECT
                users_lilyuser.last_name,
                count(deals_deal.id) as NrOfDeals
            FROM
                public.users_lilyuser,
                public.deals_deal
            WHERE
                deals_deal.assigned_to_id = users_lilyuser.id AND
                deals_deal.next_step_date < now() - interval '7 days' AND
                deals_deal.next_step_date > now() - interval '60 days' AND
                deals_deal.tenant_id = {tenant_id} AND
                deals_deal.is_deleted = false AND
                (deals_deal.status_id = {status_id_open} or deals_deal.status_id = {status_id_proposal_sent})
            GROUP BY
               users_lilyuser.first_name, users_lilyuser.last_name
            ORDER BY
               users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id,
            status_id_open=deal_status_open.pk,
            status_id_proposal_sent=deal_status_proposal_sent.pk
        )


class DealsWon(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        try:
            deal_status = DealStatus.objects.get(name='Won')
        except DealStatus.DoesNotExist:
            return ''

        return '''
            SELECT
                users_lilyuser.last_name,
                count(deals_deal.id) as NrOfDealsWon,
                sum(deals_deal.amount_recurring) as TotalAmountDealsWon,
                ROUND(sum(deals_deal.amount_recurring)/count(deals_deal.id),2) as AvgPerDealWon
            FROM
                public.users_lilyuser,
                public.deals_deal
            WHERE
                deals_deal.assigned_to_id = users_lilyuser.id AND
                deals_deal.closed_date > now() - interval '30 days month' AND
                deals_deal.tenant_id = {tenant_id} AND
                deals_deal.is_deleted = false AND
                deals_deal.new_business = true AND
                deals_deal.status_id = {status_id}
            GROUP BY
                users_lilyuser.last_name
            ORDER BY
                users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id, status_id=deal_status.pk
        )


class DealsLost(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        try:
            deal_status = DealStatus.objects.get(name='Lost')
        except DealStatus.DoesNotExist:
            return ''

        return '''
            SELECT
                users_lilyuser.last_name,
                count(deals_deal.id) as NrOfNotWonDeals,
                sum(deals_deal.amount_recurring) as TotalAmountNotWonDeals,
                ROUND(sum(deals_deal.amount_recurring)/count(deals_deal.id),2) as AvgPerNotWonDeal
            FROM
                public.users_lilyuser,
                public.deals_deal
            WHERE
                deals_deal.assigned_to_id = users_lilyuser.id AND
                deals_deal.closed_date > now() - interval '30 days month' AND
                deals_deal.tenant_id = {tenant_id} AND
                deals_deal.status_id = {status_id} AND
                deals_deal.is_deleted = false AND
                deals_deal.new_business = true
            GROUP BY
                users_lilyuser.last_name,deals_deal.new_business
            ORDER BY
                users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id, status_id=deal_status.pk
        )


class DealsAmountRecurring(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        try:
            deal_status = DealStatus.objects.get(name='Won')
        except DealStatus.DoesNotExist:
            return ''

        return '''
            SELECT
                users_lilyuser.last_name,
                count(deals_deal.id) as NrOfWonDeals,
                sum(deals_deal.amount_recurring) as TotalAmountWonDeals,
                ROUND(sum(deals_deal.amount_recurring)/count(deals_deal.id),2) as AvgPerWonDeal,
                deals_deal.new_business
            FROM
                public.users_lilyuser,
                public.deals_deal
            WHERE
                deals_deal.assigned_to_id = users_lilyuser.id AND
                deals_deal.closed_date > now() - interval '30 days month' AND
                deals_deal.is_deleted = false AND
                deals_deal.tenant_id = {tenant_id} AND
                deals_deal.new_business = false AND
                deals_deal.status_id = {status_id}
            GROUP BY
                users_lilyuser.last_name,deals_deal.new_business
            ORDER BY
                users_lilyuser.last_name,deals_deal.new_business;
        '''.format(
            tenant_id=request.user.tenant_id, status_id=deal_status.pk
        )
