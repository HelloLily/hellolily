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

CaseListController.$inject = ['$filter', '$scope', '$state', '$timeout', 'Case', 'HLFilters', 'LocalStorage',
    'Settings', 'User', 'UserTeams'];
function CaseListController($filter, $scope, $state, $timeout, Case, HLFilters, LocalStorage,
                            Settings, User, UserTeams) {
    var vm = this;

    vm.storage = new LocalStorage('cases');
    vm.storedFilterSpecialList = vm.storage.get('filterSpecialListSelected', null);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);

    Settings.page.setAllTitles('list', 'cases');

    /**
     * Table object: stores all the information to correctly display the table.
     */
    vm.table = {
        page: 1,  // Current page of pagination: 1-index.
        pageSize: 60,  // Number of items per page.
        totalItems: 0, // Total number of items.
        order: vm.storage.get('order', {
            descending: true,
            column: 'expires',  // String: current sorted column.
        }),
        visibility: vm.storage.get('visibility', {
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
        dueDateFilter: vm.storage.get('dueDateFilter', ''),
        usersFilter: vm.storage.get('usersFilter', ''),
        searchQuery: vm.storage.get('searchQuery', ''),
    };
    vm.displayFilterClear = false;
    vm.displaySpecialFilterClear = false;
    vm.filterList = [];
    vm.filterSpecialList = [];
    vm.users = [];
    vm.showEmptyState = false;

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.updateModel = updateModel;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough.
        $timeout(function() {
            _getFilterOnList();
            _getFilterSpecialList();
            _setupWatchers();
            showEmptyState();
        }, 50);
    }

    function updateModel(data, field) {
        return Case.updateModel(data, field).then(function() {
            _updateCases();
        });
    }

    /**
     * setSearchQuery() sets the search query of the table.
     *
     * @param queryString string: string that will be set as the new search query on the table.
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    /**
     * showEmptyState is used to count the total amount of cases used to show or not
     * show the empty state.
     *
     */
    function showEmptyState() {
        Case.query({}, function(data) {
            if (data.pagination.total === 0) {
                vm.showEmptyState = true;
            }
        });
    }

    /**
     * Gets the filter list. Merges selections with locally stored values.
     *
     * @returns filterList (object): object containing the filter list.
     */
    function _getFilterOnList() {
        var filterList;

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (vm.storedFilterList) {
            vm.filterList = vm.storedFilterList;
        }

        // But we still update the list afterwards (in case a filter was changed).
        filterList = [
            {
                name: 'Assigned to me',
                value: 'assigned_to.id:' + $scope.currentUser.id,
                selected: false,
            },
            {
                name: 'Assigned to nobody',
                value: 'NOT(assigned_to.id:*)',
                selected: false,
            },
            {
                name: 'Archived',
                value: '',
                selected: false,
                id: 'is_archived',
            },
        ];

        UserTeams.mine(function(teams) {
            var myTeamIds = [];

            if (teams.length) {
                // Get a list with id's of all my teams.
                teams.forEach(function(team) {
                    myTeamIds.push(team.id);
                });

                // Create a filter for cases assigned to one of my teams.
                filterList.push({
                    name: 'My teams\' cases',
                    value: 'assigned_to_teams:(' + myTeamIds.join(' OR ') + ')',
                    selected: false,
                });
            }

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * Gets the case type filter list. Merges selections with locally stored values.
     *
     * @returns filterSpecialList (object): object containing the filter list.
     */
    function _getFilterSpecialList() {
        Case.getCaseTypes(function(caseTypes) {
            var filterList = [];

            // Get a list with all case types and add each one as a filter.
            angular.forEach(caseTypes, function(caseType) {
                filterList.push({
                    name: caseType.name,
                    value: 'type.id:' + caseType.id,
                    selected: false,
                    isSpecialFilter: true,
                });
            });

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, vm.storedFilterSpecialList);

            vm.filterSpecialList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage.
     */
    function _updateTableSettings() {
        vm.storage.put('searchQuery', vm.table.searchQuery);
        vm.storage.put('archived', vm.table.archived);
        vm.storage.put('order', vm.table.order);
        vm.storage.put('visibility', vm.table.visibility);
        vm.storage.put('filterListSelected', vm.filterList);
        vm.storage.put('filterSpecialSelected', vm.filterSpecialList);
    }

    /**
     * _updateCases() reloads the cases through a service.
     *
     * Updates table.items and table.totalItems.
     */
    function _updateCases() {
        Case.getCases(
            vm.table.order.column,
            vm.table.order.descending,
            vm.table.filterQuery,
            vm.table.searchQuery,
            vm.table.page,
            vm.table.pageSize
        ).then(function(data) {
            vm.table.items = data.objects;
            vm.table.totalItems = data.total;
        });
    }

    function _setupWatchers() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of cases.
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.descending',
            'vm.table.searchQuery',
            'vm.table.archived',
            'vm.table.filterQuery',
        ], function() {
            _updateTableSettings();
            _updateCases();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache.
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the stored values are loaded,
         * the filterQuery changes and a new set of cases is fetched.
         */
        $scope.$watch('vm.filterList', function() {
            updateFilterQuery();

            vm.selectedFilters = $filter('filter')(vm.filterList, {selected: true});
        }, true);

        $scope.$watchCollection('vm.filterSpecialList', function() {
            updateFilterQuery();
        });

        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            updateFilterQuery();
            vm.storage.put('dueDateFilter', vm.table.dueDateFilter);
            vm.storage.put('usersFilter', vm.table.usersFilter);
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm, true);
    }

    function clearFilters(clearSpecial) {
        HLFilters.clearFilters(vm, clearSpecial);
    }
}
