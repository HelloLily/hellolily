import logging

from django.conf import settings
from django.db.models.query_utils import Q
from elasticsearch.exceptions import RequestError
from elasticutils import S

from lily.accounts.models import Account
from lily.messaging.email.models.models import EmailAccount
from lily.search.connections_utils import get_es_client


logger = logging.getLogger(__name__)


class LilySearch(object):
    """
    Search API for Elastic search backend.
    """

    def __init__(self, tenant_id, model_type=None, sort=None, page=0, size=10):
        """
        Setup of search.

        Arguments:
            tenant_id (int): ID of the tenant
            model_type (string): limit the search to a model
            sort (string): sort option for results
            page (int): page number of pagination
            size (int): max number of returned results
        """
        search_request = S().es(get_es_client()).indexes(settings.ES_INDEXES['default'])
        self.search = search_request.all()

        # Always filter on Tenant.
        self.raw_filters = [{
            'term': {
                'tenant': tenant_id
            }
        }]

        # Filter on model type.
        self.model_type = model_type

        # Add sorting.
        if sort:
            self.search = self.search.order_by(sort)

        # Pagination.
        from_hits = page * size
        to_hits = (page + 1) * size
        self.search = self.search[from_hits:to_hits]

    def do_search(self, return_fields=None):
        """
        Execute the search.

        Arguments:
            return_fields (list): strings of fieldnames to return from result

        Returns:
            hits (list): dicts with search results per item
            count (int): total number of results
            took (int): milliseconds Elastic search took to get the results
        """
        if settings.ES_DISABLED:
            return [], 0, 0
        self.search = self.search.filter_raw({'and': self.raw_filters})
        if self.model_type:
            self.search = self.search.doctypes(self.model_type)

        # Fire off search.
        try:
            hits = []
            execute = self.search.execute()
            for result in execute:
                hit = {
                    'id': result.id,
                }
                if not self.model_type:
                    # We will add type if not specifically searched on it.
                    hit['type'] = result.es_meta.type
                for field in result:
                    # Add specified fields, or all fields when not specified.
                    if return_fields:
                        if field in return_fields:
                            hit[field] = result[field]
                    else:
                        hit[field] = result[field]
                hits.append(hit)
            return hits, execute.count, execute.took
        except RequestError as e:
            # This can happen when the query is malformed. For example:
            # A user entering special characters. This should normally be taken
            # care of where the request is built (usually in Javascript),
            # by escaping or omitting special characters.
            # This may be hard to get fool proof, therefore we also
            # catch the exception here to prevent server errors.
            logger.error('request error %s' % e)
            return [], 0, 0

    def query_common_fields(self, query):
        """
        Set a raw_query based on common indexed fields.

        Arguments:
            query (string): query tokens
        """
        if query.strip():
            raw_query = {
                'multi_match': {
                    'query': query,
                    'type': 'cross_fields',
                    'operator': 'and',
                    'analyzer': 'cross_analyzer',
                    'fields': [
                        'id',
                        'tag',
                        'email',
                        'account_name',
                        'assigned_to',
                        'created_by',
                        'subject',
                        'name',
                        'stage_name',
                        'status',
                        'type',
                        'phone_*',
                        'contact_name',
                        'account_email',
                        'sender_email_address',
                        'sender_name',
                        'received_by_email_address',
                        'received_by_name',
                        'received_by_cc_email_address',
                        'received_by_cc_name',
                        'subject',
                        'snippet',
                        'message_id',
                        'thread_id',
                        'body',
                        'content',
                        'author',
                        'about_name',
                    ],
                },
            }
            self.search = self.search.query_raw(raw_query)

    def filter_query(self, filterquery):
        """
        Add a filterquery to the raw_filters.

        Arguments:
            filterquery (string): filterquery query_string
        """
        self.raw_filters.append({
            'query': {
                'query_string': {
                    'query': filterquery,
                    'default_operator': 'AND',
                }
            }
        })

    def account_related(self, account_id):
        """
        Search email related to an account.

        Args:
            account_id (integer): search with this account's email addresses
        """
        account = Account.objects.get(id=account_id)
        emails = [email.email_address for email in account.email_addresses.all() if email.email_address]
        contacts = account.get_contacts()
        for contact in contacts:
            contact_emails = [email.email_address for email in contact.email_addresses.all() if email.email_address]
            emails.extend(contact_emails)
        if not emails:
            # Disable results if no email at all for account.
            self.raw_filters.append({
                'limit': {
                    'value': 0
                }
            })
            return
        # Enclose emails with quotes.
        emails = ['"%s"' % email for email in emails]
        join = ' OR '.join(emails)
        filterquery = 'sender_email:(%s) OR received_by_email:(%s) OR received_by_cc_email:(%s)' % (join, join, join)
        self.filter_query(filterquery)

    def user_email_related(self, user):
        """
        Search emails that the user is allowed to see.

        Args:
            user (User): The user to use with the search
        """
        email_accounts = EmailAccount.objects.filter(
            Q(owner=user) |
            Q(public=True) |
            Q(shared_with_users__id=user.pk)
        ).filter(tenant=user.tenant, is_deleted=False).distinct('id')

        if not email_accounts:
            # Disable results if no email at all for account.
            self.raw_filters.append({
                'limit': {
                    'value': 0
                }
            })
            return
        email_accounts = set(['%s' % email.email_address for email in email_accounts])
        join = ' OR '.join(email_accounts)
        filterquery = 'account_email:(%s)' % join
        self.filter_query(filterquery)

    def get_by_id(self, id_arg):
        """
        Add a 'ids' query to the raw_filters.

        Arguments:
            id_arg (string): the ID to add
        """
        self.raw_filters.append({'ids': {'values': [id_arg]}})
