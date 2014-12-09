from django.conf import settings
from elasticutils import S


class LilySearch(object):
    """
    Search API for Elastic search backend

    Properties:
        model_type (string): limit the search to a model
    """
    model_type = None

    def __init__(self, tenant_id, id_arg=None, model_type=None, sort=None, page=0, size=None):
        """
        Setup of search

        Arguments:
            tenant_id (int): ID of the tenant
            id_arg (string): specific ID to search for
            model_type (string): limit the search to a model
            sort (string): sort option for results
            page (int): page number of pagination
            size (int): max number of returned results
        """
        search_request = S().es(urls=settings.ES_URLS).indexes(settings.ES_INDEXES['default'])
        self.search = search_request.all()

        self.raw_filters = []

        # Always filter on Tenant
        self.raw_filters.append(
            {
                'term': {
                    'tenant': tenant_id
                }
            }
        )

        # Filter on specific ids
        if id_arg:
            self.raw_filters.append({'ids': {'values': [id_arg]}})

        # Filter on model type
        if model_type:
            self.model_type = model_type
            self.search = self.search.doctypes(model_type)

        # Add sorting, if none given, sort on modified DESC
        if sort:
            self.search = self.search.order_by(sort)
        else:
            self.search = self.search.order_by('-modified')

        # Pagination
        if page != None and size:
            from_hits = page * size
            to_hits = (page + 1) * size
            self.search = self.search[from_hits:to_hits]
        else:
            # TODO: Ugly, needs a better way to make unlimited search
            self.search = self.search[0:1000000000]

    def do_search(self, return_fields):
        """
        Execute the search

        Arguments:
            return_fields (list): strings of fieldnames to return from result

        Returns:
            hits (list): dicts with search results per item
            count (int): total number of results
            took (int): milliseconds Elastic search took to get the results
        """
        self.search = self.search.filter_raw({'and': self.raw_filters})

        # Fire off search
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
                # Add specified fields, or all fields when not specified
                if return_fields:
                    if field in return_fields:
                        hit[field] = result[field]
                else:
                    hit[field] = result[field]
            hits.append(hit)

        return hits, execute.count, execute.took

    def raw_query(self, query=None, return_fields=None):
        """
        Search with a query

        Arguments:
            return_fields (list): strings of fieldnames to return from result

        Returns:
            hits (list): dicts with search results per item
            count (int): total number of results
            took (int): milliseconds Elastic search took to get the results
        """
        if query:
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

            # Prefix query is not analyzed on ES side, so split up into different tokens
            for token in query.split(' '):
                raw_query['bool']['should'].extend([
                    {
                        'prefix': {
                            'tag': token,
                        }
                    },
                    {
                        'prefix': {
                            'email*': token,
                        }
                    },
                    {
                        'prefix': {
                            'account_name': token,
                        }
                    },
                ])

            self.search = self.search.query_raw(raw_query)

        return self.do_search(return_fields)

    def filter_query(self, filterquery=None, return_fields=None):
        """
        Search with a filterquery

        Arguments:
            return_fields (list): strings of fieldnames to return from result

        Returns:
            hits (list): dicts with search results per item
            count (int): total number of results
            took (int): milliseconds Elastic search took to get the results
        """
        if filterquery:
            self.raw_filters.append({
                'query': {
                    'query_string': {
                        'query': filterquery,
                        'default_operator': 'AND',
                    }
                }
            })

        return self.do_search(return_fields)
