angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$http', '$resource', '$q', 'AccountDetail', 'ContactDetail', 'HLUtils', 'UserTeams'];
function Case($http, $resource, $q, AccountDetail, ContactDetail, HLUtils, UserTeams) {
    var Case = $resource(
        '/api/cases/case/:id',
        {},
        {
            query: {
                url: '/search/search/?type=cases_case&filterquery=:filterquery',
                isArray: true,
                transformResponse: function(data) {
                    var data = angular.fromJson(data);
                    var objects = [];
                    if (data && data.hits && data.hits.length > 0) {
                        data.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }
                    return objects;
                },
            },
            update: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            caseTypes: {
                isArray: true,
                url: 'api/cases/types/',
            },
            caseStatuses: {
                isArray: true,
                url: '/api/cases/statuses/',
            },
        }
    );

    Case.create = create;
    Case.getCases = getCases;
    Case.getCaseTypes = getCaseTypes;
    Case.getMyCasesWidget = getMyCasesWidget;
    Case.getCallbackRequests = getCallbackRequests;
    Case.getUnassignedCasesForTeam = getUnassignedCasesForTeam;
    Case.clean = clean;

    // Hardcoded because these are the only case priorities.
    Case.casePriorities = [
        {position: 0, name: 'Low'},
        {position: 1, name: 'Medium'},
        {position: 2, name: 'High'},
        {position: 3, name: 'Critical'},
    ];

    /////////

    function create() {
        var expires = moment().add(1, 'week').format();  // default expiry date is a week from now
        var teams = [];

        UserTeams.mine().$promise.then(function(userTeams) {
            angular.forEach(userTeams, function(team) {
                teams.push(team.id);
            });
        });

        return new Case({
            billing_checked: false,
            assigned_to_groups: teams,
            priority: 0,
            expires: expires,
            tags: [],
        });
    }

    /**
     * Clean the case data.
     * @param data (object): The case that's being created/updated.
     */
    function clean(data) {
        var cleanedData = angular.copy(data);

        angular.forEach(cleanedData, function(fieldValue, field) {
            if (fieldValue) {
                // We don't want to send whole objects to the API, because they're not accepted.
                // So loop through all fields and extract IDs.
                if (fieldValue.constructor === Array) {
                    var ids = [];

                    angular.forEach(fieldValue, function(item) {
                        if (typeof item === 'object') {
                            if (item.hasOwnProperty('id')) {
                                ids.push(item.id);
                            }
                        } else if (typeof item === 'number') {
                            // Seems to be an ID, so just add it to the ID array.
                            ids.push(item);
                        }
                    });

                    cleanedData[field] = ids;
                } else if (typeof fieldValue === 'object') {
                    if (fieldValue.hasOwnProperty('id')) {
                        cleanedData[field] = fieldValue.id;
                    }
                }
            }
        });

        return cleanedData;
    }

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
    function getCases(queryString, page, pageSize, orderColumn, orderedAsc, archived, filterQuery) {
        return $http({
            url: '/search/search/',
            method: 'GET',
            params: {
                type: 'cases_case',
                q: queryString,
                page: page - 1,
                size: pageSize,
                sort: HLUtils.getSorting(orderColumn, orderedAsc),
                filterquery: filterQuery,
            },
        }).then(function(response) {
            return {
                cases: response.data.hits,
                total: response.data.total,
            };
        });
    }

    function getCaseTypes() {
        return $http({
            url: '/cases/casetypes/',
            method: 'GET',
        }).then(function(response) {
            return response.data.casetypes;
        });
    }

    /**
     * Service to return a resource for my cases widget
     */
    function getMyCasesWidget(field, descending, dueDateFilter, usersFilter) {
        var deferred = $q.defer();
        var filterQuery = 'archived:false AND NOT casetype_name:Callback';

        if (dueDateFilter) {
            filterQuery += ' AND ' + dueDateFilter;
        }

        if (usersFilter) {
            filterQuery += ' AND (' + usersFilter + ')';
        } else {
            filterQuery += ' AND assigned_to_id:' + currentUser.id;
        }

        Case.query({
            filterquery: filterQuery,
            sort: HLUtils.getSorting(field, descending),
            size: 100,
        }, function(cases) {
            deferred.resolve(cases);
        });

        return deferred.promise;
    }

    function getUnassignedCasesForTeam(teamId, field, descending) {
        var filterQuery = 'archived:false AND _missing_:assigned_to_id AND assigned_to_groups:' + teamId;

        return Case.query({
            filterquery: filterQuery,
            sort: HLUtils.getSorting(field, descending),
        }).$promise;
    }

    /**
     * Gets all cases with the 'callback' case type
     *
     * @returns cases with the callback case type
     */
    function getCallbackRequests(field, descending) {
        var filterQuery = 'archived:false AND casetype_name:Callback AND assigned_to_id:' + currentUser.id;
        var deferred = $q.defer();

        Case.query({
            filterquery: filterQuery,
            sort: HLUtils.getSorting(field, descending),
        }, function(cases) {
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

    return Case;
}
