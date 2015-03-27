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
    'EmailServices'
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
        url: '/{id:int}',
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
    function($filter, $scope, $state, $stateParams, $q, AccountDetail, CaseDetail, ContactDetail, DealDetail, EmailAccount, EmailDetail, NoteDetail) {

        var id = $stateParams.id;

        $scope.opts = {historyType: ''};
        $scope.historyTypes = [
            {type: '', name: 'All'},
            {type: 'deal', name: 'Deals'},
            {type: 'case', name: 'Cases'},
            {type: 'email', name: 'Emails'},
            {type: 'note', name: 'Notes'}
        ];

        $scope.showMoreText = 'Show more';

        var add = 10;
        var size = add;
        var currentSize = 0;

        $scope.deleteAccount = function(id) {
            if (confirm('Are you sure?')) {
                AccountDetail.delete({
                    id:id
                }, function() {  // On success
                    $state.go('base.accounts');
                }, function(error) {  // On error
                    alert('something went wrong.')
                });
            }
        };

        $scope.history = [];
        function loadHistory(account, tenantEmails) {
            var history = [];
            var notesPromise = NoteDetail.query({
                filterquery: 'content_type:account AND object_id:' + id,
                size: size,
            }).$promise;

            var casesPromise = CaseDetail.query({filterquery: 'account:' + id, size: size}).$promise;
            var dealsPromise = DealDetail.query({filterquery: 'account:' + id, size: size}).$promise;
            var emailPromise = EmailDetail.query({account_related: account.id, size: size}).$promise;

            // Get all history types and add them to a common history
            $q.all([notesPromise, emailPromise, casesPromise, dealsPromise]).then(function(results) {
                var notes = results[0];
                notes.forEach(function(note) {
                    note.historyType = 'note';
                    note.color = 'yellow';
                    history.push(note);
                });
                var emails = results[1];
                emails.forEach(function(email) {
                    email = $.extend(email, {historyType: 'email', color: 'green', date: email.sent_date, right: false});
                    // Check if the sender is from tenant.
                    tenantEmails.forEach(function(emailAddress) {
                        if (emailAddress.email_address === email.sender_email) {
                            email.right = true;
                        }
                    });
                    history.push(email);
                });
                var cases = results[2];
                cases.forEach(function(caseItem) {
                    caseItem = $.extend(caseItem, {historyType: 'case', color: 'grey', date: caseItem.expires});
                    history.push(caseItem);
                    NoteDetail.query({filterquery: 'content_type:case AND object_id:' + caseItem.id, size: 5})
                    .$promise.then(function(notes) {
                        caseItem.notes = notes;
                    });
                });
                var deals = results[3];
                deals.forEach(function(deal) {
                    deal = $.extend(deal, {historyType: 'deal', color: 'blue', date: deal.closing_date});
                    history.push(deal);
                    NoteDetail.query({filterquery: 'content_type:deal AND object_id:' + deal.id, size: 5})
                    .$promise.then(function(notes) {
                            deal.notes = notes;
                    });
                });

                $scope.history.splice(0, $scope.history.length);
                // Sort all history items on date and add them to the scope.
                $filter('orderBy')(history, 'date', true).forEach(function(item) {
                    $scope.history.push(item);
                });
                $scope.limitSize = size;
                size += add;
                if ($scope.history.length === 0) {
                    $scope.showMoreText = 'No history (refresh)';
                }
                else if ($scope.history.length <= currentSize || $scope.history.length < size / 4) {
                    $scope.showMoreText = 'End reached (refresh)';
                }
                currentSize = $scope.history.length;
            });
        }

        var accountPromise = AccountDetail.get({id: id}).$promise;

        accountPromise.then(function(account) {
            $scope.account = account;
            $scope.conf.pageTitleBig = account.name;
            $scope.conf.pageTitleSmall = 'change is natural';
            HLSelect2.init();
        });

        var tenantEmailsPromise = EmailAccount.query();
        $scope.loadHistoryFromButton = function() {
            $q.all([accountPromise, tenantEmailsPromise]).then(function(results) {
                loadHistory(results[0], results[1]);
            });
        };
        $scope.loadHistoryFromButton();

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
         * updateAccounts() reloads the accounts trough a service
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
    },
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
    }
]);
