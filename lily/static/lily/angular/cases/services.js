/**
 * caseServices is a container for all case related Angular services
 */
var caseservices = angular.module('caseServices', ['ngResource']);

/**
 * $resource for Case model, now only used for detail page.
 */
caseservices.factory('CaseDetail', ['$resource', function($resource) {
    return $resource(
        '/search/search/?type=cases_case&filterquery=id\::id',
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
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = []
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj)
                        });
                    }
                    return objects;
                }
            },
            totalize: {
                url: '/search/search/?type=cases_case&size=0&filterquery=:filterquery',
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
}]);

/**
 * Case Service makes it possible to get Cases from search backend
 *
 * @returns: Case object: object with functions related to Cases
 */
caseservices.factory('Case', ['$http', function($http) {
        // TODO: LILY-660: Refactor this to other structure
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
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          cases list: paginated cases objects
     *          total int: total number of case objects
     *      }
     */
    var getCases = function(queryString, page, pageSize, orderColumn, orderedAsc, archived, filterQuery) {
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
                filterquery: filterQuery
            }
        })
        .then(function(response) {
            return {
                cases: response.data.hits,
                total: response.data.total
            };
        });
    };

    Case.getCaseTypes = function () {
        return $http({
            url: '/cases/casetypes/',
            method: 'GET'
        }).then(function (response) {
            return response.data.casetypes;
        });
    };

    /**
     * Service to return a resource for my cases widget
     */
    Case.getMyCasesWidget = function () {
        return $http({
            url: '/api/cases/user/?not_status=Closed&not_type=Callback',
            method: 'GET'
        }).then(function (response) {
            return response.data;
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
        return getCases(table.searchQuery, table.page, table.pageSize, table.order.column, table.order.ascending, table.archived, table.filterQuery);
        };

        /**
         * Gets all cases with the 'callback' case type
         *
         * @returns cases with the callback case type
         */
        Case.getCallbackRequests = function () {
            return $http({
                url: '/api/cases/user?type=Callback&archived=false',
                method: 'GET'
            }).then(function (response) {
                return {
                    callbackRequests: response.data
                };
            });
    };


    return Case;
}]);


/**
 * UnassignedTeamCases endpoint gets all unassigned cases from all teams.
 */
caseservices.factory('UnassignedTeamCases', ['$resource', function($resource) {
    return $resource('/api/cases/teams/:teamId/?is_assigned=False')
}]);

