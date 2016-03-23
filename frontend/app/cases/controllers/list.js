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

CaseListController.$inject = ['$q', '$scope', '$state', '$timeout', '$uibModal', 'Case', 'HLFilters', 'LocalStorage',
    'Settings', 'UserTeams'];
function CaseListController($q, $scope, $state, $timeout, $uibModal, Case, HLFilters, LocalStorage, Settings,
                            UserTeams) {
    var storage = LocalStorage('cases');
    var vm = this;

    Settings.page.setAllTitles('list', 'cases');

    /**
     * Table object: stores all the information to correctly display the table.
     */
    vm.table = {
        page: 1,  // Current page of pagination: 1-index.
        pageSize: 60,  // Number of items per page.
        totalItems: 0, // Total number of items.
        order: storage.get('order', {
            descending: true,
            column: 'expires',  // String: current sorted column.
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
        usersFilter: storage.get('usersFilter', ''),
        searchQuery: storage.get('searchQuery', ''),
    };
    vm.displayFilterClear = false;
    vm.displaySpecialFilterClear = false;
    vm.filterList = [];
    vm.filterCaseTypeList = [];

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;
    vm.assignTo = assignTo;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough.
        $timeout(function() {
            _getFilterOnList();
            _getFilterCaseTypeList();
            _setupWatchers();
        }, 50);
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
     * Gets the case type filter list. Merges selections with locally stored values.
     *
     * @returns filterCaseTypeList (object): object containing the filter list.
     */
    function _getFilterCaseTypeList() {
        var storedFilterList = storage.get('filterCaseTypeListSelected', null);

        Case.caseTypes(function(caseTypes) {
            var filterList = [];

            // Get a list with all case types and add each one as a filter.
            angular.forEach(caseTypes, function(caseType) {
                filterList.push({
                    name: caseType.type,
                    value: 'casetype_id:' + caseType.id,
                    selected: false,
                    isSpecialFilter: true,
                });
            });

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, storedFilterList);

            vm.filterCaseTypeList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * Gets the filter list. Merges selections with locally stored values.
     *
     * @returns filterList (object): object containing the filter list.
     */
    function _getFilterOnList() {
        var storedFilterList = storage.get('filterListSelected', null);
        var filterList;

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (storedFilterList) {
            vm.filterList = storedFilterList;
        }

        // But we still update the list afterwards (in case a filter was changed).
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

        UserTeams.mine(function(teams) {
            var myTeamIds = [];
            var filters = [];

            // Get a list with id's of all my teams.
            teams.forEach(function(team) {
                myTeamIds.push(team.id);
            });

            // Create a filter for case assigned to one of my teams.
            filterList.push({
                name: 'My teams cases',
                value: 'assigned_to_groups:(' + myTeamIds.join(' OR ') + ')',
                selected: false,
            });

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, storedFilterList);

            vm.filterList = filterList;

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
        storage.put('filterCaseTypeListSelected', vm.filterCaseTypeList);
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
            vm.table.order.descending,
            vm.table.filterQuery
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
         * the filterQuery changes and a new set of deals is fetched.
         */
        $scope.$watchCollection('vm.filterList', function() {
            updateFilterQuery();
        });

        $scope.$watchCollection('vm.filterCaseTypeList', function() {
            updateFilterQuery();
        });

        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            updateFilterQuery();
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm, true);
    }

    function clearFilters(clearSpecial) {
        HLFilters.clearFilters(vm, clearSpecial);
    }

    function assignTo(myCase) {
        var modalInstance = $uibModal.open({
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
