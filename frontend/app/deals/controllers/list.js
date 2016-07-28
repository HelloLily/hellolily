angular.module('app.deals').config(dealsConfig);

dealsConfig.$inject = ['$stateProvider'];
function dealsConfig($stateProvider) {
    $stateProvider.state('base.deals', {
        url: '/deals',
        views: {
            '@': {
                templateUrl: 'deals/controllers/list.html',
                controller: DealListController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Deals',
        },
    });
}

angular.module('app.deals').controller('DealListController', DealListController);

DealListController.$inject = ['$filter', '$scope', '$timeout', 'Deal', 'HLFilters', 'LocalStorage',
    'Settings', 'Tenant'];
function DealListController($filter, $scope, $timeout, Deal, HLFilters, LocalStorage,
                            Settings, Tenant) {
    var vm = this;

    vm.storage = new LocalStorage('deals');
    vm.storedFilterSpecialList = vm.storage.get('filterSpecialListSelected', null);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);

    Settings.page.setAllTitles('list', 'deals');

    /**
     * Table object: stores all the information to correctly display the table
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filterQuery: '',
        archived: vm.storage.get('archived', false),
        order: vm.storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        visibility: vm.storage.get('visibility', {
            deal: true,
            client: true,
            status: true,
            created: true,
            name: true,
            amountOnce: true,
            amountRecurring: true,
            assignedTo: true,
            nextStep: true,
            nextStepDate: true,
            newBusiness: true,
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

    vm.updateFilterQuery = updateFilterQuery;
    vm.setSearchQuery = setSearchQuery;
    vm.clearFilters = clearFilters;

    activate();

    //////

    function activate() {
        // This timeout is needed because by loading from LocalStorage isn't fast enough
        $timeout(function() {
            _setupWatchers();
            _getFilterOnList();
            _getFilterSpecialList();
        }, 50);

        Tenant.query({}, function(tenant) {
            vm.tenant = tenant;
        });
    }

    function _getFilterOnList() {
        var filterList;

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (vm.storedFilterList) {
            vm.filterList = vm.storedFilterList;
        }

        // But we still update the list afterwards (in case a filter was changed)
        filterList = [
            {
                name: 'Assigned to me',
                value: 'assigned_to.id:' + currentUser.id,
                selected: false,
            },
            {
                name: 'New business',
                value: 'new_business:true',
                selected: false,
            },
            {
                name: 'Age between 7 and 30 days',
                value: 'created:[' + moment().subtract(30, 'd').format('YYYY-MM-DD') + ' TO ' + moment().subtract(7, 'd').format('YYYY-MM-DD') + ']',
                selected: false,
            },
            {
                name: 'Age between 30 and 120 days',
                value: 'created:[' + moment().subtract(120, 'd').format('YYYY-MM-DD') + ' TO ' + moment().subtract(30, 'd').format('YYYY-MM-DD') + ']',
                selected: false,
            },
            {
                name: 'Archived',
                value: '',
                selected: false,
                id: 'is_archived',
            },
        ];

        Deal.getStatuses(function(response) {
            angular.forEach(response.results, function(status) {
                filterList.push({
                    name: status.name,
                    value: 'status.id:' + status.id,
                    selected: false,
                });
            });

            // Merge previous stored selection with new filters.
            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * Gets the deal next step filter list. Merges selections with locally stored values.
     *
     * @returns filterSpecialList (object): object containing the filter list.
     */
    function _getFilterSpecialList() {
        Deal.getNextSteps(function(response) {
            var filterList = [];

            angular.forEach(response.results, function(nextStep) {
                filterList.push({
                    name: nextStep.name,
                    value: 'next_step.id:' + nextStep.id,
                    selected: false,
                    position: nextStep.position,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterSpecialList);

            // Update filterList once AJAX calls are done.
            vm.filterSpecialList = filterList;

            // Watch doesn't get triggered here, so manually call _updateTableSettings.
            _updateTableSettings();
        });
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage
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
     * _updateDeals() reloads the deals through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateDeals() {
        Deal.getDeals(
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
         * needs a new set of deals
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
            _updateDeals();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('vm.table.visibility', function() {
            _updateTableSettings();
        });

        /**
         * Watches the filters so when the values are retrieved from local storage,
         * the filterQuery changes and a new set of deals is fetched
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

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */
    function setSearchQuery(queryString) {
        vm.table.searchQuery = queryString;
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm, true);
    }

    function clearFilters(clearSpecial) {
        HLFilters.clearFilters(vm, clearSpecial);
    }
}
