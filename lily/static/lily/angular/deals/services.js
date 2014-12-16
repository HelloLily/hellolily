/**
 * dealServices is a container for all deal related Angular services
 */
angular.module('dealServices', [])

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
         * @param queryString string: current filter on the deallist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of deals
         * @param orderedAsc {boolean}: current ordering
         * @param archived {boolean}: when true, only archived are fetched, if false, only active
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          deals list: paginated deals objects
         *          total int: total number of deal objects
         *      }
         */
        var getDeals = function(queryString, page, pageSize, orderColumn, orderedAsc, archived) {

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
                    filterquery: archived ? 'archived:true' : 'archived:false'
                }
            })
                .then(function(response) {
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
            return getDeals(table.filter, table.page, table.pageSize, table.order.column, table.order.ascending, table.archived);
        };

        return Deal;
    }]);
