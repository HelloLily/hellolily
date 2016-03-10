import anyjson
from django.db import connection
from django.http import HttpResponse
from django.views.generic import View

from lily.utils.views import LoginRequiredMixin


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict
    """
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


class RawDatabaseView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        query = self.get_query(request, *args, **kwargs)

        cursor = connection.cursor()
        cursor.execute(query)

        results = self.parse_results(dictfetchall(cursor))

        return HttpResponse(anyjson.dumps(results))

    def get_query(self, request, *args, **kwargs):
        raise NotImplementedError

    def parse_results(self, results):
        parsed_results = []
        for row in results:
            parsed_row = {}
            for key, value in row.iteritems():
                parsed_row[key] = str(value)
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
                cases_case_assigned_to_groups
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_groups.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_groups.lilygroup_id = {lilygroup_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN  date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second';
        '''.format(
            tenant_id=request.user.tenant_id,
            lilygroup_id=int(kwargs['lilygroup_id']),
        )


class CasesPerTypeCountLastWeek(RawDatabaseView):

    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count(cases_case.id),
                type,
                date_trunc( 'week', now() - interval '1 week' ) as from,
                (date_trunc('week', now() - interval '1 week' ) + interval '1 week' - interval '1 second') as to,
                EXTRACT(WEEK FROM date_trunc( 'week', now() - interval '1 week' )) as weeknr
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_groups
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_groups.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_groups.lilygroup_id = {lilygroup_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN  date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second'
            GROUP BY
                type;
        '''.format(
            tenant_id=request.user.tenant_id,
            lilygroup_id=int(kwargs['lilygroup_id']),
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
                cases_case_assigned_to_groups,
                tags_tag
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_groups.case_id AND
                cases_case.id = tags_tag.object_id AND
                tags_tag.name != '' AND
                tags_tag.tenant_id = {tenant_id} AND
                cases_case_assigned_to_groups.lilygroup_id = {lilygroup_id} AND
                cases_case.is_deleted = false AND

                /*last week*/
                cases_case.created BETWEEN date_trunc( 'week', now() - interval '1 week' ) AND
                date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second';
        '''.format(
            tenant_id=request.user.tenant_id,
            lilygroup_id=int(kwargs['lilygroup_id']),
        )


class CasesCountPerStatus(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                count (cases_case.id), cases_casestatus.status
            FROM
                cases_case,
                cases_casestatus,
                cases_casetype,
                cases_case_assigned_to_groups
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_groups.case_id AND
                cases_case.tenant_id = {tenant_id} AND
                cases_case_assigned_to_groups.lilygroup_id = {lilygroup_id} AND
                cases_case.is_deleted = false AND
                cases_case.is_archived = false AND
                cases_casestatus.status != 'Closed'
            GROUP BY
                cases_casestatus.status;
          '''.format(
            tenant_id=request.user.tenant_id,
            lilygroup_id=int(kwargs['lilygroup_id']),
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
                cases_case_assigned_to_groups,
                tags_tag
            WHERE
                cases_case.status_id = cases_casestatus.id AND
                cases_case.type_id = cases_casetype.id AND
                cases_case.id = cases_case_assigned_to_groups.case_id AND
                cases_case.id = tags_tag.object_id AND
                tags_tag.name <> '' AND
                tags_tag.tenant_id = {tenant_id} AND
                cases_case.is_deleted = false AND
                cases_case.created BETWEEN date_trunc('month', now()- interval '1 month') AND
                date_trunc('month', now()) - interval '1 second' AND
                cases_case_assigned_to_groups.lilygroup_id = {lilygroup_id} AND
                cases_casetype.type != 'Config' AND
                cases_casetype.type != 'Retour' AND
                cases_casetype.type != 'Callback'
            GROUP BY
                tags_tag.name
            HAVING
                COUNT (tags_tag.name) > 2
            ORDER BY
                count(tags_tag.name) desc
            LIMIT 15;
          '''.format(
            tenant_id=request.user.tenant_id,
            lilygroup_id=int(kwargs['lilygroup_id']),
        )


class DealsUnsentFeedbackForms(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
        return '''
            SELECT
                users_lilyuser.last_name,
                count(deals_deal.id) as NrOfDeals
            FROM
                deals_deal,
                users_lilyuser
            WHERE
                deals_deal.assigned_to_id = users_lilyuser.id AND
                deals_deal.status = 2 AND
                deals_deal.new_business = true AND
                deals_deal.closed_date BETWEEN (now() - interval '120 day') AND (now() - interval '30 day') AND
                deals_deal.feedback_form_sent = false AND
                /* deals_deal.card_sent = true AND */
                deals_deal.tenant_id = {tenant_id} AND
                deals_deal.is_deleted = false
            GROUP BY
                users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id
        )


class DealsUrgentFollowUp(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
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
                (deals_deal.status = 0 or deals_deal.status = 1)
            GROUP BY
               users_lilyuser.first_name, users_lilyuser.last_name
            ORDER BY
               users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id
        )


class DealsWon(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
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
                deals_deal.status = 2
            GROUP BY
                users_lilyuser.last_name
            ORDER BY
                users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id
        )


class DealsLost(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
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
                deals_deal.status = 3 AND
                deals_deal.is_deleted = false AND
                deals_deal.new_business = true
            GROUP BY
                users_lilyuser.last_name,deals_deal.new_business
            ORDER BY
                users_lilyuser.last_name;
        '''.format(
            tenant_id=request.user.tenant_id
        )


class DealsAmountRecurring(RawDatabaseView):
    def get_query(self, request, *args, **kwargs):
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
                deals_deal.status = 2
            GROUP BY
                users_lilyuser.last_name,deals_deal.new_business
            ORDER BY
                users_lilyuser.last_name,deals_deal.new_business;
        '''.format(
            tenant_id=request.user.tenant_id
        )
