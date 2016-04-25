angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$resource', '$q', 'Account', 'Contact', 'HLUtils'];
function Case($resource, $q, Account, Contact, HLUtils) {
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
            getCaseTypes: {
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
    _case.getMyCasesWidget = getMyCasesWidget;
    _case.getCallbackRequests = getCallbackRequests;
    _case.getCasePriorities = getCasePriorities;

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
        }, function(results) {
            angular.forEach(results.objects, function(callbackCase) {
                if (callbackCase.account) {
                    Account.get({id: callbackCase.account}, function(account) {
                        if (account.phone_numbers.length) {
                            callbackCase.accountPhone = account.phone_numbers[0].number;
                        }
                    });
                }

                if (callbackCase.contact) {
                    Contact.get({id: callbackCase.contact}, function(contact) {
                        if (contact.phone_numbers.length) {
                            callbackCase.contactPhone = contact.phone_numbers[0].number;
                        }
                    });
                }
            });

            deferred.resolve(results);
        });

        return deferred.promise;
    }

    function getCasePriorities() {
        // Hardcoded because these are the only case priorities.
        return [
            {id: 0, name: 'Low'},
            {id: 1, name: 'Medium'},
            {id: 2, name: 'High'},
            {id: 3, name: 'Critical'},
        ];
    }

    return _case;
}
