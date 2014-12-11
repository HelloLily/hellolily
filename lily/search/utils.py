from django.conf import settings
from elasticutils import S


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
        search_request = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES['default'])
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
        self.search = self.search.filter_raw({'and': self.raw_filters})
        if self.model_type:
            self.search = self.search.doctypes(self.model_type)

        # Fire off search.
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

    def raw_query(self, query):
        """
        Set a raw_query based on common indexed fields.

        Arguments:
            query (string): query tokens (space separated)
        """
        raw_query = {
            'bool': {
                'should': [
                    {
                        'multi_match': {
                            'query': query,
                            'operator': 'and',
                            'fields': [
                                'name',
                                'assigned_to',
                            ],
                        }
                    },
                ]
            }
        }

        # Prefix query is not analyzed on ES side, so split up into different tokens.
        for token in query.split(' '):
            for prefix_field in ['tag', 'email*', 'account_name', 'subject', 'body']:
                raw_query['bool']['should'].extend([
                    {
                        'prefix': {
                            prefix_field: token,
                        }
                    },
                ])

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

    def get_by_id(self, id_arg):
        """
        Add a 'ids' query to the raw_filters.

        Arguments:
            id_arg (string): the ID to add
        """
        self.raw_filters.append({'ids': {'values': [id_arg]}})
