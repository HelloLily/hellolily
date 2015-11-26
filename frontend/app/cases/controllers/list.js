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

CaseListController.$inject = ['$modal', '$scope', '$state', '$timeout', 'Settings', 'Case', 'LocalStorage',
    'UserTeams', '$q'];
function CaseListController($modal, $scope, $state, $timeout, Settings, Case, LocalStorage, UserTeams, $q) {
    var storage = LocalStorage('caseList');
    var vm = this;

    vm.openPostponeWidget = Case.openPostponeWidget;

    Settings.page.setAllTitles('list', 'cases');

    /**
     * table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 60,  // number of items per page
        totalItems: 0, // total number of items
        order: storage.get('order', {
            ascending: true,
            column: 'expires',  // string: current sorted column
        }),
        visibility: storage.get('visibility', {
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
            tags: true,
        }),
        dueDateFilter: storage.get('dueDateFilter', ''),
        searchQuery: storage.get('searchQuery', ''),
    };
    vm.displayTypeFilterClear = false;
    vm.displayNonTypeFilterClear = false;
    vm.filterList = [];

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearNonTypeFilters = clearNonTypeFilters;
    vm.clearTypeFilters = clearTypeFilters;
    vm.assignTo = assignTo;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough
        $timeout(function() {
            _getFilterList();
            _setupWatchers();
        }, 50);
    }

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    function _displayClearButtons() {
        vm.displayTypeFilterClear = false;
        vm.displayNonTypeFilterClear = false;
        vm.filterList.forEach(function(filter) {
            if (filter.selected) {
                if (filter.isTypeFilter) {
                    vm.displayTypeFilterClear = true;
                } else {
                    vm.displayNonTypeFilterClear = true;
                }
            }
        });
    }

    /**
     * Gets the filter list. Merges selections with locally stored values.
     *
     * @returns filterList (object): object containing the filter list
     */
    function _getFilterList() {
        var storedFilterList = storage.get('filterListSelected', null);
        var filterList;
        var teamsCall;
        var casesCall;

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (storedFilterList) {
            vm.filterList = storedFilterList;
            _displayClearButtons();
        }

        // But we still update the list afterwards (in case a filter was changed)
        filterList = [
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
                name: 'Archived',
                value: '',
                selected: false,
                id: 'archived',
            },
        ];

        teamsCall = UserTeams.mine().$promise.then(function(teams) {
            var myTeamIds = [];
            var filters = [];
            teams.forEach(function(team) {
                myTeamIds.push(team.id);
            });

            filters.push({
                name: 'My teams cases',
                value: 'assigned_to_groups:(' + myTeamIds.join(' OR ') + ')',
                selected: false,
            });

            return filters;
        });

        casesCall = Case.getCaseTypes().then(function(cases) {
            var filters = [];
            angular.forEach(cases, function(caseName, caseId) {
                filters.push({
                    name: 'Case type ' + caseName,
                    value: 'casetype_id:' + caseId,
                    selected: false,
                    isTypeFilter: true,
                });
            });

            return filters;
        });

        // Wait for all promises.
        $q.all([teamsCall, casesCall]).then(function(subFilterLists) {
            subFilterLists.forEach(function(subFilterList) {
                subFilterList.forEach(function(filter) {
                    filterList.push(filter);
                });
            });

            if (storedFilterList) {
                // Stored filter list exists, merge the selections from with the stored values.
                angular.forEach(storedFilterList, function(storedFilter) {
                    angular.forEach(filterList, function(caseInList) {
                        if (storedFilter.name === caseInList.name) {
                            caseInList.selected = storedFilter.selected;
                        }
                    });
                });
            }

            // Update filterList once AJAX calls are done.
            vm.filterList = filterList;
            _displayClearButtons();

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage
     */
    function _updateTableSettings() {
        storage.put('searchQuery', vm.table.searchQuery);
        storage.put('archived', vm.table.archived);
        storage.put('order', vm.table.order);
        storage.put('visibility', vm.table.visibility);
        storage.put('filterListSelected', vm.filterList);
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
        ).then(function(data) {
            vm.table.items = data.cases;
            vm.table.totalItems = data.total;
        });
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
         * Watches the filters so when the stored values are loaded,
         * the filterQuery changes and a new set of deals is fetched
         */
        $scope.$watchCollection('vm.filterList', function() {
            updateFilterQuery();
        });

        $scope.$watch('vm.table.dueDateFilter', function() {
            updateFilterQuery();
        });
    }

    function updateFilterQuery() {
        /*
        * Update the filter based on the separate filters.
        */
        var typeFilterStrings = [];
        var nonTypeFilterStrings = [];
        _displayClearButtons();
        vm.table.filterQuery = '';

        vm.filterList.forEach(function(filter) {
            if (filter.id && filter.id === 'archived') {
                if (!filter.selected) {
                    nonTypeFilterStrings.push('archived:false');
                }
            } else {
                if (filter.selected) {
                    if (filter.isTypeFilter) {
                        typeFilterStrings.push(filter.value);
                    } else {
                        nonTypeFilterStrings.push(filter.value);
                    }
                }
            }
        });

        if (vm.table.dueDateFilter) {
            nonTypeFilterStrings.push(vm.table.dueDateFilter);
        }

        // If we have type filter, we join them OR-wise.
        if (typeFilterStrings.length > 0) {
            nonTypeFilterStrings.push('(' + typeFilterStrings.join(' OR ') + ')');
        }

        // Finally join all filters AND-wise.
        vm.table.filterQuery = nonTypeFilterStrings.join(' AND ');
    }

    function clearNonTypeFilters() {
        vm.filterList.forEach(function(filter) {
            if (!filter.isTypeFilter) {
                filter.selected = false;
            }
        });

        updateFilterQuery();
    }

    function clearTypeFilters() {
        vm.filterList.forEach(function(filter) {
            if (filter.isTypeFilter) {
                filter.selected = false;
            }
        });

        updateFilterQuery();
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
