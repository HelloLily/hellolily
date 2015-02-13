/**
 * dealServices is a container for all deal related Angular services
 */
angular.module('dealServices', [])

    /**
     * $resource for Deal model, now only used for detail page.
     */
    .factory('DealDetail', ['$resource', function($resource) {
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
    }])

    /**
     * Deal Service makes it possible to get Deals from search backend
     *
     * @returns: Deal object: object with functions related to Deals
     */
    .factory('Deal', ['$http', function($http) {
        var Deal = {};

        /**
         * getDeals() gets the deals from the search backend trough a promise
         *
         * @param queryString string: current search query on the deallist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of deals
         * @param orderedAsc {boolean}: current ordering
         * @param archived {boolean}: when true, only archived are fetched, if false, only active
         * @param filterQuery {string}: contains the filters which are used in ElasticSearch
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          deals list: paginated deals objects
         *          total int: total number of deal objects
         *      }
         */
        var getDeals = function (queryString, page, pageSize, orderColumn, orderedAsc, archived, filterQuery) {
            // Check if there's a filter set
            if (filterQuery !== '') {
                // Check if we're looking for archived cases or not
                if (archived) {
                    filterQuery += ' AND archived:true';
                }
                else {
                    filterQuery += ' AND archived:false';
                }
            }
            else {
                // Otherwise only check if we're displaying archived cases or not
                filterQuery = archived ? 'archived:true' : 'archived:false';
            }

            var sort = '';
            if (orderedAsc) sort += '-';
            sort += orderColumn;

            return $http({
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'deals_deal',
                    q: queryString,
                    page: page - 1,
                    size: pageSize,
                    sort: sort,
                    filterquery: filterQuery
                }
            }).then(function (response) {
                return {
                    deals: response.data.hits,
                    total: response.data.total
                };
            });
        };

        /**
         * query() makes it possible to query on deals on backend search
         *
         * @param table object: holds all the info needed to get deals from backend
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          deals list: paginated deal objects
         *          total int: total number of deal objects
         *      }
         */
        Deal.query = function(table) {
            return getDeals(table.searchQuery, table.page, table.pageSize, table.order.column, table.order.ascending, table.archived, table.filterQuery);
        };

        return Deal;
    }]);
