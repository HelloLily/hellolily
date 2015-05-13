(function () {
    'use strict';

    /**
     * dealServices is a container for all deal related Angular services
     */
    angular.module('app.deals.services', []);

    /**
     * $resource for Deal model, now only used for detail page.
     */
    angular.module('app.deals.services').factory('DealDetail', DealDetail);

    DealDetail.$inject = ['$resource'];
    function DealDetail ($resource) {
        return $resource(
            '/search/search/?type=deals_deal&filterquery=id\::id',
            {},
            {
                get: {
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        if (data && data.hits && data.hits.length > 0) {
                            var obj = data.hits[0];
                            return obj;
                        }
                        return null;
                    }
                },
                query: {
                    url: '/search/search/?type=deals_deal&filterquery=:filterquery',
                    isArray: true,
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        var objects = [];
                        if (data && data.hits && data.hits.length > 0) {
                            data.hits.forEach(function(obj) {
                                obj = $.extend(obj, {historyType: 'deal', color: 'blue', date: obj.modified});
                                objects.push(obj)
                            });
                        }
                        return objects;
                    }
                },
                totalize: {
                    url: '/search/search/?type=deals_deal&size=0&filterquery=:filterquery',
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        if (data && data.total) {
                            return {total: data.total};
                        }
                        return {total: 0};
                    }
                }
            }
        );
    }

    angular.module('app.deals.services').factory('DealStages', DealStages);

    DealStages.$inject = ['$resource'];

    function DealStages ($resource) {
        return $resource('/api/deals/stages');
    }

    /**
     * Deal Service makes it possible to get Deals from search backend
     *
     * @returns: Deal object: object with functions related to Deals
     */
    angular.module('app.deals.services').factory('Deal', Deal);

    Deal.$inject = ['$http', '$resource'];
    function Deal ($http, $resource) {
        var Deal = $resource(
            '/api/deals/deal/:id',
            null,
            {
                update: {
                    method: 'PUT',
                    params: {
                        id: '@id'
                    }
                },
                query: {
                    url: '/search/search/',
                    method: 'GET',
                    params:
                    {
                        type: 'deals_deal'
                    },
                    isArray: true,
                    transformResponse: function(data) {
                        data = angular.fromJson(data);
                        var objects = [];
                        if (data && data.hits && data.hits.length > 0) {
                            data.hits.forEach(function(obj) {
                                obj = $.extend(obj, {
                                    historyType: 'deal',
                                    color: 'blue',
                                    date: obj.modified,
                                    total_size: data.total
                                });
                                objects.push(obj)
                            });
                        }
                        return objects;
                    }
                }
            }
        );

        Deal.getDeals = getDeals;
        Deal.getDealsToCheck = getDealsToCheck;
        Deal.prototype.markDealAsChecked = markDealAsChecked;

        /////

        /**
         * getDeals() gets the deals from the search backend through a promise
         *
         * @param queryString string: current search query on the deallist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of deals
         * @param orderedAsc {boolean}: current ordering
         * @param filterQuery {string}: contains the filters which are used in ElasticSearch
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          deals list: paginated deals objects
         *          total int: total number of deal objects
         *      }
         */
        function getDeals (queryString, page, pageSize, orderColumn, orderedAsc, filterQuery) {
            var sort = '';
            if (orderedAsc) sort += '-';
            sort += orderColumn;

            return Deal.query({
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: sort,
                filterquery: filterQuery
            }, function (deals) {
                if (deals.length) {
                    return {
                        deals: deals,
                        total: deals[0].total_size
                    };
                }
            }).$promise;
        }

        function getDealsToCheck (column, ordering, userId) {

            var filterQuery = 'stage:2 AND is_checked:false';
            if (userId) {
                filterQuery += ' AND assigned_to_id:' + userId;
            }
            return getDeals('', 1, 20, column, ordering, filterQuery);
        }

        function markDealAsChecked () {
            var deal = this;
            deal.is_checked = true;
            return deal.$update();
        }

        return Deal;
    }
})();
