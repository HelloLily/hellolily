angular.module('app.cases.services').factory('Case', Case);

Case.$inject = ['$resource', 'CacheFactory', 'HLCache', 'HLResource', 'HLUtils'];
function Case($resource, CacheFactory, HLCache, HLResource, HLUtils) {
    var _case = $resource(
        '/api/cases/:id/',
        {},
        {
            search: {
                url: '/search/search/',
                method: 'GET',
                params: {
                    type: 'cases_case',
                },
                transformResponse: function(data) {
                    let jsonData = angular.fromJson(data);
                    let objects = [];
                    let total = 0;

                    if (jsonData) {
                        if (jsonData.hits && jsonData.hits.length > 0) {
                            jsonData.hits.forEach(function(obj) {
                                objects.push(obj);
                            });
                        }

                        total = jsonData.total;
                    }

                    return {
                        objects: objects,
                        total: total,
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
                cache: CacheFactory.get('dataCache'),
                url: '/api/cases/types/',
            },
            getStatuses: {
                cache: CacheFactory.get('dataCache'),
                url: '/api/cases/statuses/',
                transformResponse: function(data) {
                    var statusData = angular.fromJson(data);

                    angular.forEach(statusData.results, function(status) {
                        if (status.name === 'Closed') {
                            _case.closedStatus = status;
                        }
                    });

                    return statusData;
                },
            },
            query: {
                isArray: false,
            },
        }
    );

    _case.create = create;
    _case.getCases = getCases;
    _case.getCasePriorities = getCasePriorities;
    _case.updateModel = updateModel;

    _case.getStatuses();

    /////////

    function create() {
        var expires = moment().add(1, 'week');  // default expiry date is a week from now

        return new _case({
            billing_checked: false,
            priority: 0,
            expires: expires,
            tags: [],
        });
    }

    function updateModel(data, field, caseObject) {
        var patchPromise;
        var args = HLResource.createArgs(data, field, caseObject);

        if (field === 'name') {
            Settings.page.setAllTitles('detail', data);
        }

        if (args.hasOwnProperty('priority')) {
            // Automatically increment expiry date based on the priority.
            let casePriorities = _case.getCasePriorities();
            let expireDate = HLUtils.addBusinessDays(casePriorities[args.priority].date_increment);
            expireDate = moment(expireDate).format('YYYY-MM-DD');
            args.expires = expireDate;
        }

        patchPromise = HLResource.patch('Case', args).$promise;

        if (caseObject) {
            patchPromise.then((response) => {
                caseObject.expires = response.expires;
            });
        }

        return patchPromise;
    }

    /**
     * getCases() gets the cases from the search backend through a promise
     *
     * @param orderColumn {string}: Current sorting of cases.
     * @param orderedAsc {boolean}: Current ordering.
     * @param filterQuery {string}: Contains the filters which are used in Elasticsearch.
     * @param searchQuery {string}: Current filter on the caselist.
     * @param page {number=1}: Current page of pagination.
     * @param pageSize {number=100}: Current page size of pagination.
     *
     * @returns Promise object: when promise is completed:
     *      {
     *          cases {Array}: Paginated cases objects.
     *          total {number}: Total number of case objects.
     *      }
     */
    function getCases(orderColumn, orderedAsc, filterQuery, searchQuery = '', page = 1, pageSize = 100) {
        return _case.search({
            q: searchQuery,
            page: page - 1,
            size: pageSize,
            sort: HLUtils.getSorting(orderColumn, orderedAsc),
            filterquery: filterQuery,
        }, function(data) {
            return data;
        }).$promise;
    }

    function getCasePriorities() {
        // Hardcoded because these are the only case priorities.
        return [
            {id: 0, name: 'Low', date_increment: 5},
            {id: 1, name: 'Medium', date_increment: 3},
            {id: 2, name: 'High', date_increment: 1},
            {id: 3, name: 'Critical', date_increment: 0},
        ];
    }

    return _case;
}
