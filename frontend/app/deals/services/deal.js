angular.module('app.deals.services').factory('Deal', Deal);

Deal.$inject = ['$resource', 'HLUtils', 'HLForms', 'HLCache', 'CacheFactory'];
function Deal($resource, HLUtils, HLForms, HLCache, CacheFactory) {
    var _deal = $resource(
        '/api/deals/:id/',
        null,
        {
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
                transformRequest: function(data) {
                    var jsonData = angular.copy(data);
                    return angular.toJson(HLForms.clean(jsonData));
                },
            },
            save: {
                method: 'POST',
                transformRequest: function(data) {
                    var jsonData = angular.copy(data);
                    return angular.toJson(HLForms.clean(jsonData));
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
                transformRequest: function(data) {
                    var jsonData = angular.copy(data);
                    return angular.toJson(HLForms.clean(jsonData));
                },
            },
            query: {
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'deals_deal',
                },
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];

                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            var deal = $.extend(obj, {
                                historyType: 'deal',
                                color: 'blue',
                                date: obj.modified,
                                total_size: jsonData.total,
                            });

                            objects.push(deal);
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
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
        }
    );

    _deal.getDeals = getDeals;
    _deal.create = create;
    _deal.prototype.markDealAsChecked = markDealAsChecked;

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
            assigned_to: {id: currentUser.id, full_name: currentUser.fullName},
        });
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

        return _deal.query({
            q: searchQuery,
            page: page - 1,
            size: pageSize,
            sort: sort,
            filterquery: filterQuery,
        }, function(data) {
            return data;
        }).$promise;
    }

    function markDealAsChecked() {
        var deal = this;
        deal.is_checked = true;
        return deal.$update();
    }

    return _deal;
}
