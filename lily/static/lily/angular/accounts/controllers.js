/**
 * accountControllers is a container for all account related Controllers
 */
angular.module('accountControllers', [
    // Angular dependencies
    'ngCookies',

    // 3rd party
    'ui.bootstrap',

    // Lily dependencies
    'accountServices',
    'contactServices',
    'caseServices',
    'dealServices',
    'noteServices',
    'emailServices'
])

    /**
     * AccountDetailController is a controller to show details of an account.
     */
    .controller('AccountDetailController', [
        'AccountDetail',
        'CaseDetail',
        'DealDetail',
        'ContactDetail',
        'NoteDetail',
        'EmailDetail',
        'EmailAccount',
        '$scope',
        '$q',
        '$filter',
        function(Account, Case, Deal, Contact, Note, Email, EmailAccount, $scope, $q, $filter) {
            $scope.showMoreText = 'Show more';
            var id = window.location.pathname;
            if (id.substr(-1) == '/') {
                id = id.substr(0, id.length - 1);
            }
            id = id.substr(id.lastIndexOf('/') + 1);

            var add = 10,
                size = add,
                currentSize = 0;
            $scope.history = [];
            function loadHistory(account, tenantEmails) {
                var history = [];
                var notesPromise = Note.query({
                    filterquery: 'content_type:account AND object_id:' + id,
                    size: size
                }).$promise;
                var casesPromise = Case.query({
                    filterquery: 'account:' + id,
                    size: size
                }).$promise;
                var dealsPromise = Deal.query({
                    filterquery: 'account:' + id,
                    size: size
                }).$promise;
                var emailPromise = Email.query  ({
                    account_related: account.id,
                    size: size
                }).$promise;
                $q.all([notesPromise, emailPromise, casesPromise, dealsPromise]).then(function(results) {
                    var notes = results[0];
                    notes.forEach(function(note) {
                        note.note = true;
                        history.push(note);
                    });
                    var emails = results[1];
                    emails.forEach(function(email) {
                        email.email = true;
                        email.date = email.sent_date;
                        email.right = false;
                        // Check if the sender is from tenant.
                        tenantEmails.forEach(function(emailAddress) {
                            if (emailAddress.email_address == email.sender_email) {
                                email.right = true;
                            }
                        });
                        history.push(email);
                    });
                    var cases = results[2];
                    cases.forEach(function(caseItem) {
                        caseItem.caseItem = true;
                        caseItem.date = caseItem.expires;
                        history.push(caseItem);
                    });
                    var deals = results[3];
                    deals.forEach(function(deal) {
                        deal.deal = true;
                        deal.date = deal.closing_date;
                        history.push(deal);
                    });

                    $scope.history.splice(0, $scope.history.length);
                    $filter('orderBy')(history, 'date', true).forEach(function(item) {
                        $scope.history.push(item);
                    });
                    $scope.history.splice(size, $scope.history.length);
                    size += add;
                    if ($scope.history.length == 0) {
                        $scope.showMoreText = 'No history (refresh)';
                    }
                    else if ($scope.history.length <= currentSize || $scope.history.length < size / 4) {
                        $scope.showMoreText = 'End reached (refresh)';
                    }
                    currentSize = $scope.history.length;
                });
            }

            var accountPromise = Account.get({id: id}).$promise;
            accountPromise.then(function(account) {
                $scope.account = account;
            });
            var tenantEmailsPromise = EmailAccount.query();
            $scope.loadHistoryFromButton = function() {
                $q.all([accountPromise, tenantEmailsPromise]).then(function(results) {
                    loadHistory(results[0], results[1]);
                });
            };
            $scope.loadHistoryFromButton();

            Case.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
                $scope.numCases = total.total;
            });

            Deal.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
                $scope.numDeals = total.total;
            });

            Contact.query({filterquery: 'account:' + id}).$promise.then(function(contacts) {
                $scope.workers = contacts;
            });
        }
    ])

    /**
     * AccountListController controller to show list of accounts
     *
     */
    .controller('AccountListController', [
        '$scope',
        '$cookieStore',
        '$window',

        'Account',
        'Cookie',
        function($scope, $cookieStore, $window, Account, Cookie) {

            Cookie.prefix ='accountList';

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
            $scope.$watchGroup([
                'table.page',
                'table.order.column',
                'table.order.ascending',
                'table.filter'
            ], function() {
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

                // Open url
                $window.open(url);
            }
        }
    ]
);
