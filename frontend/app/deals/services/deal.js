angular.module('app.deals.services').factory('Deal', Deal);

Deal.$inject = ['$resource', 'CacheFactory', 'HLCache', 'HLForms', 'HLResource', 'HLUtils'];
function Deal($resource, CacheFactory, HLCache, HLForms, HLResource, HLUtils) {
    var _deal = $resource(
        '/api/deals/:id/',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            save: {
                method: 'POST',
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            search: {
                url: '/api/deals/',
                method: 'GET',
                transformResponse: function(data) {
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.results && jsonData.results.length > 0) {
                            jsonData.results.forEach(function(obj) {
                                var deal = $.extend(obj, {
                                    activityType: 'deal',
                                    color: 'blue',
                                    date: obj.modified,
                                    total_size: jsonData.total,
                                });

                                objects.push(deal);
                            });
                        }

                        total = jsonData.pagination.total;
                    }

                    return {
                        objects: objects,
                        total: total,
                    };
                },
            },
            getNextSteps: {
                cache: CacheFactory.get('dataCache'),
                url: 'api/deals/next-steps/',
            },
            getWhyCustomer: {
                cache: CacheFactory.get('dataCache'),
                url: 'api/deals/why-customer/',
            },
            getWhyLost: {
                cache: CacheFactory.get('dataCache'),
                url: 'api/deals/why-lost',
            },
            getStatuses: {
                url: '/api/deals/statuses/',
                cache: CacheFactory.get('dataCache'),
                transformResponse: function(data) {
                    var statusData = angular.fromJson(data);

                    angular.forEach(statusData.results, function(status) {
                        if (status.name === 'Lost') {
                            _deal.lostStatus = status;
                        } else if (status.name === 'Won') {
                            _deal.wonStatus = status;
                        }
                    });

                    return statusData;
                },
            },
            getFoundThrough: {
                cache: CacheFactory.get('dataCache'),
                url: '/api/deals/found-through/',
            },
            getContactedBy: {
                cache: CacheFactory.get('dataCache'),
                url: '/api/deals/contacted-by/',
            },
            getFormOptions: {
                url: 'api/deals',
                method: 'OPTIONS',
            },
            query: {
                isArray: false,
            },
            getDocuments: {
                url: '/api/integrations/documents/:contact/',
            },
        }
    );

    _deal.getDeals = getDeals;
    _deal.create = create;
    _deal.updateModel = updateModel;

    _deal.getStatuses();

    /////////

    function create() {
        return new _deal({
            new_business: false,
            twitter_checked: false,
            is_checked: false,
            card_sent: false,
            tags: [],
            currency: 'EUR',
            amount_once: '0',
            amount_recurring: '0',
            assigned_to: null,
        });
    }

    function updateModel(data, field, deal) {
        var patchPromise;
        var args = HLResource.createArgs(data, field, deal);

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        patchPromise = HLResource.patch('Deal', args).$promise;

        if (deal) {
            patchPromise.then((response) => {
                if (response.hasOwnProperty('next_step')) {
                    deal.next_step_date = response.next_step_date;
                }
            });
        }

        return patchPromise;
    }

    /**
     * Get the deals from the search backend through a promise.
     *
     * @param orderColumn {string}: Current sorting of deals.
     * @param orderedDesc {boolean}: Current ordering.
     * @param filterQuery {string}: Contains the filters which are used in Elasticsearch.
     * @param searchQuery {string}: Current search query on the deal list.
     * @param page {number=1}: Current page of pagination.
     * @param pageSize {number=100}: Current page size of pagination.
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          deals {list}: Paginated deals objects.
     *          total {number}: Total number of deal objects.
     *      }
     */
    function getDeals(orderColumn, orderedDesc, filterQuery, searchQuery = '', page = 1, pageSize = 100) {
        var sort = HLUtils.getSorting(orderColumn, orderedDesc);

        return _deal.search({
            search: searchQuery,
            page: page,
            page_size: pageSize,
            ordering: sort,
            filterquery: filterQuery,
        }, function(data) {
            return data;
        }).$promise;
    }

    return _deal;
}
