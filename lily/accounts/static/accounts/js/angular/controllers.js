'use strict';

/**
 * AccountsControllers manages all routes and controllers
 * that relate to Account.
 */
var accountController = angular.module('AccountControllers', [
    'ngCookies',
    'ui.bootstrap',
    'ui.slimscroll',
    'AccountServices',
    'CaseServices',
    'contactServices',
    'noteServices',
    'app.email.services'
]);


/**
 * Router definition.
 */
accountController.config(['$stateProvider', function($stateProvider) {

    $stateProvider.state('base.accounts', {
        url: '/accounts',
        views: {
            '@': {
                templateUrl: 'accounts/account-list.html',
                controller: 'AccountListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Accounts'
        }
    });

    $stateProvider.state('base.accounts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'accounts/account-detail.html',
                controller: 'AccountDetailController'
            }
        },
        ncyBreadcrumb: {
            label: '{{ account.name }}'
        }
    });

    $stateProvider.state('base.accounts.create', {
        url: '/create',
        views: {
            '@': {
                templateUrl: '/accounts/create/',
                controller: 'AccountUpsertController'
            }
        },
        ncyBreadcrumb: {
            label: 'Create'
        }
    });

    $stateProvider.state('base.accounts.detail.edit', {
        url: '/edit',
        views: {
            '@': {
                templateUrl: function(elem) {
                    return '/accounts/' + elem.id + '/edit/';
                },
                controller: 'AccountUpsertController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit'
        }
    });

    $stateProvider.state('base.accounts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'AccountDeleteController'
            }
        },
    });

}]);

/**
 * Details page with historylist and more detailed contact information.
 */
accountController.controller('AccountDetailController', [
    '$filter',
    '$scope',
    '$state',
    '$stateParams',
    '$q',
    'AccountDetail',
    'CaseDetail',
    'ContactDetail',
    'DealDetail',
    'EmailAccount',
    'EmailDetail',
    'NoteDetail',
    'NoteService',

    function($filter, $scope, $state, $stateParams, $q, AccountDetail, CaseDetail, ContactDetail, DealDetail, EmailAccount, EmailDetail, NoteDetail, NoteService) {
        var id = $stateParams.id;

        $scope.account = AccountDetail.get({id: id});
        $scope.account.$promise.then(function(account) {
            $scope.account = account;
            $scope.conf.pageTitleBig = account.name;
            $scope.conf.pageTitleSmall = 'change is natural';
        });

        CaseDetail.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
            $scope.numCases = total.total;
        });

        DealDetail.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
            $scope.numDeals = total.total;
        });

        ContactDetail.query({filterquery: 'account:' + id}).$promise.then(function(contacts) {
            $scope.workers = contacts;
        });
    }
]);

/**
 * ContactListController is a controller to show list of contacts
 *
 */
accountController.controller('AccountListController', [
    '$cookieStore',
    '$scope',
    '$window',
    'Account',
    'AccountDetail',
    'Cookie',
    function($cookieStore, $scope, $window, Account, AccountDetail, Cookie) {

        Cookie.prefix ='accountList';

        $scope.conf.pageTitleBig = 'Account List';
        $scope.conf.pageTitleSmall = 'An overview of accounts';


        $scope.deleteAccount = function(account) {
            if (confirm('Are you sure?')) {
                AccountDetail.delete({
                    id:account.id
                }, function() {  // On success
                    var index = $scope.table.items.indexOf(account);
                    $scope.table.items.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        };


        /**
         * table object: stores all the information to correctly display the table
         */
        $scope.table = {
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
            })};

        /**
         * updateTableSettings() sets scope variables to the cookie
         */
        function updateTableSettings() {
            Cookie.setCookieValue('filter', $scope.table.filter);
            Cookie.setCookieValue('order', $scope.table.order);
            Cookie.setCookieValue('visibility', $scope.table.visibility);
        }

        /**
         * updateAccounts() reloads the accounts through a service
         *
         * Updates table.items and table.totalItems
         */
        function updateAccounts() {
            Account.query(
                $scope.table
            ).then(function(data) {
                    $scope.table.items = data.accounts;
                    $scope.table.totalItems = data.total;
                }
            );
        }

        /**
         * Watches the model info from the table that, when changed,
         * needs a new set of accounts
         */
        $scope.$watchGroup(['table.page', 'table.order.column', 'table.order.ascending', 'table.filter'], function() {
            updateTableSettings();
            updateAccounts();
        });

        /**
         * Watches the model info from the table that, when changed,
         * needs to store the info to the cache
         */
        $scope.$watchCollection('table.visibility', function() {
           updateTableSettings();
        });

        /**
         * setFilter() sets the filter of the table
         *
         * @param queryString string: string that will be set as the new filter on the table
         */
        $scope.setFilter = function(queryString) {
            $scope.table.filter = queryString;
        };

        /**
         * exportToCsv() creates an export link and opens it
         */
        $scope.exportToCsv = function() {
            var getParams = '';
            // If there is a filter, add it
            if ($scope.table.filter) {
                getParams += '&export_filter=' + $scope.table.filter;
            }

            // Add all visible columns
            angular.forEach($scope.table.visibility, function(value, key) {
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
        };
    }
]);

/**
 * Controller for update and new Account actions.
 */
accountController.controller('AccountUpsertController', [
    '$scope',
    '$stateParams',
    'AccountDetail',
    function($scope, $stateParams, AccountDetail) {
        var id = $stateParams.id;
        // New Account; set title.
        if(!id) {
            $scope.conf.pageTitleBig = 'New Account';
            $scope.conf.pageTitleSmall = 'change is natural';
        } else {
            // Existing Account; Get details from ES and set title.
            var accountPromise = AccountDetail.get({id: id}).$promise;
            accountPromise.then(function(account) {
                $scope.account = account;
                $scope.conf.pageTitleBig = account.name;
                $scope.conf.pageTitleSmall = 'change is natural';
                HLSelect2.init();
            });
        }
        HLDataProvider.init();
        HLFormsets.init();
    }
]);

/**
 * Controller to delete a account
 */
accountController.controller('AccountDeleteController', [
    '$state',
    '$stateParams',

    'AccountDetail',

    function($state, $stateParams, AccountDetail) {
        var id = $stateParams.id;

        AccountDetail.delete({
            id:id
        }, function() {  // On success
            $state.go('base.accounts');
        }, function(error) {  // On error
            // Error notification needed
            $state.go('base.accounts');
        });
    }
]);
