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
                (date_trunc('week', now() - interval '1 week' )+ interval '1 week' - interval '1 second') as to,
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
              count(DISTINCT(cases_case.id)), date_trunc( 'week', now() - interval '1 week' ) as start, date_trunc( 'week', now() - interval '1 week' )+ interval '1 week' - interval '1 second' as end
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
