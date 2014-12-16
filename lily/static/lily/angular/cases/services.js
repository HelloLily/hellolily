/**
 * caseServices is a container for all case related Angular services
 */
angular.module('caseServices', [])

    /**
     * Case Service makes it possible to get Cases from search backend
     *
     * @returns: Case object: object with functions related to Cases
     */
    .factory('Case', ['$http', function($http) {
        var Case = {};

        /**
         * getCases() gets the cases from the search backend trough a promise
         *
         * @param queryString string: current filter on the caselist
         * @param page int: current page of pagination
         * @param pageSize int: current page size of pagination
         * @param orderColumn string: current sorting of cases
         * @param orderedAsc {boolean}: current ordering
         * @param archived {boolean}: when true, only archived are fetched, if false, only active
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          cases list: paginated cases objects
         *          total int: total number of case objects
         *      }
         */
        var getCases = function(queryString, page, pageSize, orderColumn, orderedAsc, archived) {

            var sort = '';
            if (orderedAsc) sort += '-';
            sort += orderColumn;

            return $http({
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'cases_case',
                    q: queryString,
                    page: page - 1,
                    size: pageSize,
                    sort: sort,
                    filterquery: archived ? 'archived:true' : 'archived:false'
                }
            })
                .then(function(response) {
                    return {
                        cases: response.data.hits,
                        total: response.data.total
                    };
                });
        };

        /**
         * query() makes it possible to query on cases on backend search
         *
         * @param table object: holds all the info needed to get cases from backend
         *
         * @returns Promise object: when promise is completed:
         *      {
         *          cases list: paginated case objects
         *          total int: total number of case objects
         *      }
         */
        Case.query = function(table) {
            return getCases(table.filter, table.page, table.pageSize, table.order.column, table.order.ascending, table.archived);
        };

        return Case;
    }]);
