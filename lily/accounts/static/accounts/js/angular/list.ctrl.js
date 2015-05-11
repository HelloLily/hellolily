(function() {
    'use strict';

    /**
     * Router definition.
     */
    angular.module('app.accounts').config(accountConfig);

    accountConfig.$inject = ['$stateProvider'];

    function accountConfig ($stateProvider) {
        $stateProvider.state('base.accounts', {
            url: '/accounts',
            views: {
                '@': {
                    templateUrl: 'accounts/account-list.html',
                    controller: 'AccountList',
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'Accounts'
            }
        });
    }

    /**
     * AccountList is a controller to show list of contacts
     *
     */
    angular.module('app.accounts').controller('AccountList', AccountList);

    AccountList.$inject = ['$scope', '$window', 'Account', 'AccountDetail', 'Cookie'];
    function AccountList ($scope, $window, Account, AccountDetail, Cookie) {
        var vm = this;

        /**
         * table object: stores all the information to correctly display the table
         */
        vm.table = {
            page: 1,  // current page of pagination: 1-index
            pageSize: 20,  // number of items per page
            totalItems: 0, // total number of items
            filter: Cookie.getCookieValue('filter', ''),  // search filter
            order:  Cookie.getCookieValue('order', {
                ascending: true,
                column:  'modified'  // string: current sorted column
            }),
            visibility: Cookie.getCookieValue('visibility', {
                name: true,
                contactInformation: true,
                assignedTo: true,
                created: true,
                modified: true,
                tags: true
            })
        };
        vm.deleteAccount = deleteAccount;
        vm.setFilter = setFilter;
        vm.exportToCsv = exportToCsv;

        activate();

        /////////////

        function activate() {
            _setupWatches();
        }

        Cookie.prefix ='accountList';
        $scope.conf.pageTitleBig = 'Account List';
        $scope.conf.pageTitleSmall = 'An overview of accounts';


        function deleteAccount (account) {
            if (confirm('Are you sure?')) {
                AccountDetail.delete({
                    id:account.id
                }, function() {  // On success
                    var index = vm.table.items.indexOf(account);
                    vm.table.items.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        }

        /**
         * _updateTableSettings() sets scope variables to the cookie
         */
        function _updateTableSettings() {
            Cookie.setCookieValue('filter', vm.table.filter);
            Cookie.setCookieValue('order', vm.table.order);
            Cookie.setCookieValue('visibility', vm.table.visibility);
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
                vm.table.order.ascending
            ).then(function(data) {
                    vm.table.items = data.accounts;
                    vm.table.totalItems = data.total;
                }
            );
        }

        function _setupWatches() {
            /**
             * Watches the model info from the table that, when changed,
             * needs a new set of accounts
             */
            $scope.$watchGroup(['vm.table.page', 'vm.table.order.column', 'vm.table.order.ascending', 'vm.table.filter'], function() {
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
        function setFilter (queryString) {
            vm.table.filter = queryString;
        }

        /**
         * exportToCsv() creates an export link and opens it
         */
        function exportToCsv () {
            var getParams = '';
            // If there is a filter, add it
            if (vm.table.filter) {
                getParams += '&export_filter=' + vm.table.filter;
            }

            // Add all visible columns
            angular.forEach(vm.table.visibility, function(value, key) {
                if (value) {
                    getParams += '&export_columns='+ key;
                }
            });

            // Setup url
            var url = '/accounts/export/';
            if (getParams) {
                url += '?' + getParams.substr(1);
            }

            $window.open(url);
        }
    }
})();
