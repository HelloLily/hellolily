/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts', {
        url: '/accounts',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/list.html',
                controller: AccountList,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Accounts',
        },
        data: {
            app_name: 'accounts',
        },
    });
}

/**
 * AccountList is a controller to show list of contacts
 *
 */
angular.module('app.accounts').controller('AccountList', AccountList);

AccountList.$inject = ['$filter', '$scope', '$window', 'Settings', 'Account', 'LocalStorage', 'HLFilters', 'HLUtils'];
function AccountList($filter, $scope, $window, Settings, Account, LocalStorage, HLFilters, HLUtils) {
    var vm = this;
    vm.storage = new LocalStorage('accountList');
    vm.storedFilterList = vm.storage.get('filterListSelected', null);
    /**
     * Stores all the information to correctly display the table.
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: vm.storage.get('filter', ''),  // search filter
        order: vm.storage.get('order', {
            descending: true,
            column: 'modified',  // string: current sorted column
        }),
        visibility: vm.storage.get('visibility', {
            name: true,
            contactInformation: true,
            assignedTo: true,
            created: true,
            modified: true,
            status: true,
            tags: true,
            customerId: false,
        }),
    };
    vm.showEmptyState = false;

    vm.removeFromList = removeFromList;
    vm.filterList = [];
    vm.setFilter = setFilter;
    vm.exportToCsv = exportToCsv;

    activate();

    //////

    function activate() {
        _setupWatches();
        showEmptyState();
        _getFilterOnList();
    }

    Settings.page.setAllTitles('list', 'accounts');

    function removeFromList(account) {
        var index = vm.table.items.indexOf(account);
        vm.table.items.splice(index, 1);
        $scope.$apply();
    }

    /**
     * _updateTableSettings() puts the scope variables in local storage
     */
    function _updateTableSettings() {
        vm.storage.put('filter', vm.table.filter);
        vm.storage.put('order', vm.table.order);
        vm.storage.put('visibility', vm.table.visibility);
        vm.storage.put('filterListSelected', vm.filterList);
    }

    function _getFilterOnList() {
        var filterList = [];

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (vm.storedFilterList) {
            vm.filterList = vm.storedFilterList;
        }

        Account.getStatuses(function(response) {
            angular.forEach(response.results, function(status) {
                filterList.push({
                    name: status.name,
                    value: 'status.id:' + status.id,
                    selected: false,
                    isSpecialFilter: true,
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
     * _updateAccounts() reloads the accounts through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateAccounts() {
        let blockTarget = '#tableBlockTarget';
        HLUtils.blockUI(blockTarget, true);

        Account.getAccounts(
            vm.table.filter,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.descending,
            vm.table.filterQuery
        ).then(function(data) {
            vm.table.items = data.accounts;
            vm.table.totalItems = data.total;

            HLUtils.unblockUI(blockTarget);
        });
    }

    function _setupWatches() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup([
            'vm.table.page',
            'vm.table.order.column',
            'vm.table.order.descending',
            'vm.table.filter',
            'vm.table.filterQuery',
        ], function() {
            _updateTableSettings();
            _updateAccounts();
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
    }

    /**
     * setSearchQuery() sets the search query of the table
     *
     * @param queryString string: string that will be set as the new search query on the table
     */

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm, true);
    }


    /**
     * setFilter() sets the filter of the table
     *
     * @param queryString string: string that will be set as the new filter on the table
     */
    function setFilter(queryString) {
        vm.table.filter = queryString;
    }

    function showEmptyState() {
        // Show the empty state when there are no accounts yet.
        vm.showEmptyState = !Account.exists();
    }

    /**
     * exportToCsv() creates an export link and opens it
     */
    function exportToCsv() {
        var getParams = '';
        var url = '/accounts/export/';

        // If there is a filter, add it
        if (vm.table.filter) {
            getParams += '&export_filter=' + vm.table.filter;
        }

        // Add all visible columns
        angular.forEach(vm.table.visibility, function(value, key) {
            if (value) {
                getParams += '&export_columns=' + key;
            }
        });

        // Setup url
        if (getParams) {
            url += '?' + getParams.substr(1);
        }

        $window.open(url);
    }

    $scope.$on('$viewContentLoaded', () => {
        angular.element('.hl-search-field').focus();
    });
}
