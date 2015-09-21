angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$http', '$resource', '$q', 'AccountDetail', 'ContactDetail'];
function Case ($http, $resource, $q, AccountDetail, ContactDetail) {

    var Case = $resource(
        '/api/cases/case/:id',
        {},
        {
            query: {
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                }
            },
            update: {
                method: 'PATCH',
                params: {
                    id: '@id'
                }
            }
        }
    );

    Case.getCases = getCases;
    Case.getCaseTypes = getCaseTypes;
    Case.getMyCasesWidget = getMyCasesWidget;
    Case.getCallbackRequests = getCallbackRequests;
    Case.getUnassignedCasesForTeam = getUnassignedCasesForTeam;
    Case.getTotalCountLastWeek = getTotalCountLastWeek;
    Case.getPerTypeCountLastWeek = getPerTypeCountLastWeek;
    Case.getCountWithTagsLastWeek = getCountWithTagsLastWeek;
    Case.getCountPerStatus = getCountPerStatus;
    Case.getTopTags = getTopTags;

    return Case;

    /////////

    /**
     * getCases() gets the cases from the search backend through a promise
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
    function getCases (queryString, page, pageSize, orderColumn, orderedAsc, archived, filterQuery) {
        return $http({
            url: '/search/search/',
            method: 'GET',
            params: {
                type: 'cases_case',
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: _getSorting(orderColumn, orderedAsc),
                filterquery: filterQuery
            }
        }).then(function(response) {
            return {
                cases: response.data.hits,
                total: response.data.total
            };
        });
    }

    function getCaseTypes () {
        return $http({
            url: '/cases/casetypes/',
            method: 'GET'
        }).then(function (response) {
            return response.data.casetypes;
        });
    }

    function _getSorting (field, sorting) {
        var sort = '';
        sort += sorting ? '-': '';
        sort += field;
        return sort;
    }

    /**
     * Service to return a resource for my cases widget
     */
    function getMyCasesWidget (field, sorting, filter) {
        var deferred = $q.defer();
        var filterQuery = 'archived:false AND NOT casetype_name:Callback AND assigned_to_id:' + currentUser.id;

        if (filter) {
            filterQuery += ' AND ' + filter;
        }

        Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting),
            size: 25
        }, function (cases) {
            deferred.resolve(cases);
        });

        return deferred.promise;
    }

    /**
     * Gets all cases with the 'callback' case type
     *
     * @returns cases with the callback case type
     */
    function getCallbackRequests (field, sorting) {
        var filterQuery = 'archived:false AND casetype_name:Callback AND assigned_to_id:' + currentUser.id;
        var deferred = $q.defer();

        Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting)
        }, function (cases) {
            angular.forEach(cases, function(callbackCase) {
                if (callbackCase.account) {
                    AccountDetail.get({id: callbackCase.account}, function(account) {
                        callbackCase.accountPhone = account.phone;
                    });
                }
                if (callbackCase.contact) {
                    ContactDetail.get({id: callbackCase.contact}, function(contact) {
                        callbackCase.contactPhone = contact.phone;
                    });
                }
            });
            deferred.resolve(cases);
        });
        return deferred.promise;
    }

    function getUnassignedCasesForTeam (teamId, field, sorting) {
        var filterQuery = 'archived:false AND _missing_:assigned_to_id AND assigned_to_groups:' + teamId;

        return Case.query({
            filterquery: filterQuery,
            sort: _getSorting(field, sorting)
        }).$promise;
    }

    function getTotalCountLastWeek (lilyGroupId) {

        return $http({
            url: '/stats/cases/total/'+ lilyGroupId + '/',
            method: 'GET'
        }).then(function(response) {
            return response.data;
        });
    }

    function getPerTypeCountLastWeek (lilyGroupId) {

        return $http({
            url: '/stats/cases/grouped/'+ lilyGroupId + '/',
            method: 'GET'
        }).then(function(response) {
            return response.data;
        });
    }

    function getCountWithTagsLastWeek (lilyGroupId) {

        return $http({
            url: '/stats/cases/withtags/'+ lilyGroupId + '/',
            method: 'GET'
        }).then(function(response) {
            return response.data;
        });
    }

    function getCountPerStatus (lilyGroupId) {

        return $http({
            url: '/stats/cases/countperstatus/'+ lilyGroupId + '/',
            method: 'GET'
        }).then(function(response) {
            return response.data;
        });
    }

    function getTopTags (lilyGroupId) {

        return $http({
            url: '/stats/cases/toptags/'+ lilyGroupId + '/',
            method: 'GET'
        }).then(function(response) {
            return response.data;
        });
    }
}
