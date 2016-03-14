angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$http', '$resource', '$q', 'AccountDetail', 'ContactDetail', 'HLUtils'];
function Case($http, $resource, $q, AccountDetail, ContactDetail, HLUtils) {
    var _case = $resource(
        '/api/cases/case/:id/',
        {},
        {
            get: {
                transformResponse: function(data) {
                    var lilyCase = angular.fromJson(data);

                    if (lilyCase.contact) {
                        // API returns 'full_name' but ES returns 'name'. So get the full name and set the name.
                        lilyCase.contact.name = lilyCase.contact.full_name;
                    }

                    if (lilyCase.assigned_to) {
                        lilyCase.assigned_to.name = HLUtils.getFullName(lilyCase.assigned_to);
                    }

                    return lilyCase;
                },
            },
            query: {
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'cases_case',
                },
                transformResponse: function(data) {
                    var jsonData = angular.fromJson(data);
                    var objects = [];
                    if (jsonData && jsonData.hits && jsonData.hits.length > 0) {
                        jsonData.hits.forEach(function(obj) {
                            objects.push(obj);
                        });
                    }

                    return {
                        objects: objects,
                        total: jsonData.total,
                    };
                },
            },
            update: {
                method: 'PUT',
                params: {
                    id: '@id',
                },
            },
            patch: {
                method: 'PATCH',
                params: {
                    id: '@id',
                },
            },
            caseTypes: {
                isArray: true,
                url: '/api/cases/types/',
            },
            caseStatuses: {
                isArray: true,
                url: '/api/cases/statuses/',
            },
        }
    );

    _case.create = create;
    _case.getCases = getCases;
    _case.getCaseTypes = getCaseTypes;
    _case.getMyCasesWidget = getMyCasesWidget;
    _case.getCallbackRequests = getCallbackRequests;

    // Hardcoded because these are the only case priorities.
    _case.casePriorities = [
        {position: 0, name: 'Low'},
        {position: 1, name: 'Medium'},
        {position: 2, name: 'High'},
        {position: 3, name: 'Critical'},
    ];

    /////////

    function create() {
        var expires = moment().add(1, 'week').format();  // default expiry date is a week from now

        return new _case({
            billing_checked: false,
            priority: 0,
            expires: expires,
            tags: [],
        });
    }

    /**
     * getCases() gets the cases from the search backend through a promise
     *
     * @param queryString string: current filter on the caselist
     * @param page int: current page of pagination
     * @param pageSize int: current page size of pagination
     * @param orderColumn string: current sorting of cases
     * @param orderedAsc {boolean}: current ordering
     * @param filterQuery {string}: contains the filters which are used in ElasticSearch
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          cases list: paginated cases objects
     *          total int: total number of case objects
     *      }
     */
    function getCases(queryString, page, pageSize, orderColumn, orderedAsc, filterQuery) {
        return _case.query({
            q: queryString,
            page: page - 1,
            size: pageSize,
            sort: HLUtils.getSorting(orderColumn, orderedAsc),
            filterquery: filterQuery,
        }, function(data) {
            return data;
        }).$promise;
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

        _case.query({
            filterquery: filterQuery,
            sort: HLUtils.getSorting(field, descending),
            size: 100,
        }, function(cases) {
            deferred.resolve(cases);
        });

        return deferred.promise;
    }

    /**
     * Gets all cases with the 'callback' case type
     *
     * @returns cases with the callback case type
     */
    function getCallbackRequests(field, descending) {
        var filterQuery = 'archived:false AND casetype_name:Callback AND assigned_to_id:' + currentUser.id;
        var deferred = $q.defer();

        _case.query({
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

    return _case;
}
