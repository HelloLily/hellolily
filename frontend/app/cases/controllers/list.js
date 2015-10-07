angular.module('app.cases').config(caseConfig);

caseConfig.$inject = ['$stateProvider'];
function caseConfig($stateProvider) {
    $stateProvider.state('base.cases', {
        url: '/cases',
        views: {
            '@': {
                templateUrl: 'cases/controllers/list.html',
                controller: CaseListController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Cases',
        },
    });
}

angular.module('app.cases').controller('CaseListController', CaseListController);

CaseListController.$inject = ['$location', '$modal', '$scope', '$state', '$timeout', 'Case', 'Cookie', 'HLFilters'];
function CaseListController($location, $modal, $scope, $state, $timeout, Case, Cookie, HLFilters) {
    var cookie = Cookie('caseList');
    var vm = this;

    $scope.conf.pageTitleBig = 'Cases';
    $scope.conf.pageTitleSmall = 'do all your lookin\' here';

    /**
     * table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 60,  // number of items per page
        totalItems: 0, // total number of items
        searchQuery: '',  // search query
        order: cookie.get('order', {
            ascending: true,
            column: 'expires',  // string: current sorted column
        }),
        visibility: cookie.get('visibility', {
            caseId: true,
            client: true,
            subject: true,
            priority: true,
            type: true,
            status: true,
            expires: true,
            created: true,
            assignedTo: true,
            createdBy: true,
            tags: true
        }),
        expiresFilter: cookie.get('expiresFilter', ''),
    };
    vm.displayFilterClear = false;
    vm.filterList = [];

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.assignTo = assignTo;

    activate();

    //////

    function activate() {
        // This timeout is needed because by default getting a cookie with Angular has a delay
        $timeout(function() {
            _setSearchQuery();
            _getFilterList();
            _setupWatchers();
        }, 50);
    }

    function _setSearchQuery() {
        // Setup search query
        var searchQuery = '';

        // Check if filter is set as query parameter
        var search = $location.search().search;
        if (search != undefined) {
            searchQuery = search;
        } else {
            // Get searchQuery from cookie
            searchQuery = cookie.get('searchQuery', '');
        }
        vm.table.searchQuery = searchQuery;
    }

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    /**
     * Gets the filter list. Is either the value in the cookie or a new list
     *
     * @returns filterList (object): object containing the filter list
     */
    function _getFilterList() {
        var filterListCookie = cookie.get('filterList', null);

        if (filterListCookie) {
            // Cookie is set, so use it as the filterList
            vm.filterList = filterListCookie;
        } else {
            var filterList = [
                {
                    name: 'Assigned to me',
                    value: 'assigned_to_id:' + $scope.currentUser.id,
                    selected: false,
                },
                {
                    name: 'Assigned to nobody',
                    value: 'NOT(assigned_to_id:*)',
                    selected: false,
                },
                {
                    name: 'Expired today',
                    value: 'expires: ' + moment().subtract(1, 'd').format('YYYY-MM-DD'),
                    selected: false,
                },
                {
                    name: 'Expired 7 days or more ago',
                    value: 'expires:[* TO ' + moment().subtract(7, 'd').format('YYYY-MM-DD') + ']',
                    selected: false,
                },
                {
                    name: 'Expired 30 days or more ago',
                    value: 'expires:[* TO ' + moment().subtract(30, 'd').format('YYYY-MM-DD') + ']',
                    selected: false,
                },
                {
                    name: 'Archived',
                    value: '',
                    selected: false,
                    id: 'archived',
                },
            ];

            // Update filterList for now
            vm.filterList = filterList;

            Case.getCaseTypes().then(function(cases) {
                for (var key in cases) {
                    if (cases.hasOwnProperty(key)) {
                        filterList.push({
                            name: 'Case type ' + cases[key],
                            value: 'casetype_id:' + key,
                            selected: false,
                        });
                    }
                }

                // Update filterList once AJAX call is done
                vm.filterList = filterList;
                // Watch doesn't get triggered here, so manually call _updateTableSettings
                _updateTableSettings();
            });
        }
    }

    /**
     * _updateTableSettings() sets scope variables to the cookie
     */
    function _updateTableSettings() {
        cookie.put('searchQuery', vm.table.searchQuery);
        cookie.put('archived', vm.table.archived);
        cookie.put('order', vm.table.order);
        cookie.put('visibility', vm.table.visibility);
        cookie.put('filterList', vm.filterList);
    }

    /**
     * _updateCases() reloads the cases through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateCases() {
        Case.getCases(
            vm.table.searchQuery,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.ascending,
            vm.table.archived,
            vm.table.filterQuery
        )
            .then(function(data) {
                vm.table.items = data.cases;
                vm.table.totalItems = data.total;
            }
        );
    }

    function _setupWatchers() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of cases
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.ascending',
            'vm.table.searchQuery',
            'vm.table.archived',
            'vm.table.filterQuery',
        ], function() {
            _updateTableSettings();
            _updateCases();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the cookie is loaded,
         * the filterQuery changes and a new set of deals is fetched
         */
        $scope.$watchCollection('vm.filterList', function() {
            updateFilterQuery();
        });

        $scope.$watch('vm.table.expiresFilter', function() {
            updateFilterQuery();
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm);
    }

    function clearFilters() {
        HLFilters.clearFilters(vm);
    }

    function assignTo(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/assignto.html',
            controller: 'CaseAssignModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase;
                },
            },
        });

        modalInstance.result.then(function() {
            $state.go($state.current, {}, {reload: true});
        });
    }
}
