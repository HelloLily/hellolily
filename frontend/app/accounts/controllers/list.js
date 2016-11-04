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

AccountList.$inject = ['$scope', '$window', 'Settings', 'Account', 'LocalStorage'];
function AccountList($scope, $window, Settings, Account, LocalStorage) {
    var vm = this;
    var storage = new LocalStorage('accountList');
    /**
     * Stores all the information to correctly display the table.
     */
    vm.table = {
        page: 1,  // current page of pagination: 1-index
        pageSize: 20,  // number of items per page
        totalItems: 0, // total number of items
        filter: storage.get('filter', ''),  // search filter
        order: storage.get('order', {
            descending: true,
            column: 'modified',  // string: current sorted column
        }),
        visibility: storage.get('visibility', {
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

    vm.removeFromList = removeFromList;
    vm.setFilter = setFilter;
    vm.exportToCsv = exportToCsv;

    activate();

    /////////////

    function activate() {
        _setupWatches();
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
        storage.put('filter', vm.table.filter);
        storage.put('order', vm.table.order);
        storage.put('visibility', vm.table.visibility);
    }

    /**
     * _updateAccounts() reloads the accounts through a service
     *
     * Updates table.items and table.totalItems
     */
    function _updateAccounts() {
        Account.getAccounts(
            vm.table.filter,
            vm.table.page,
            vm.table.pageSize,
            vm.table.order.column,
            vm.table.order.descending
        ).then(function(data) {
            vm.table.items = data.accounts;
            vm.table.totalItems = data.total;
        });
    }

    function _setupWatches() {
        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup(['vm.table.page', 'vm.table.order.column', 'vm.table.order.descending', 'vm.table.filter'], function() {
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
    }


    /**
     * setFilter() sets the filter of the table
     *
     * @param queryString string: string that will be set as the new filter on the table
     */
    function setFilter(queryString) {
        vm.table.filter = queryString;
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
}
