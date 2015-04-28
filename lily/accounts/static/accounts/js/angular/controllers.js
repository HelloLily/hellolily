(function() {
    'use strict';

    /**
     * AccountsControllers manages all routes and controllers
     * that relate to Account.
     */
    angular.module('app.accounts', [
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
    angular.module('app.accounts').config(['$stateProvider', function($stateProvider) {

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
    angular.module('app.accounts').controller('AccountDetailController', [
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

            $scope.history = [];
            function loadHistory(account, tenantEmails) {
                var history = [];
                var notesPromise = NoteDetail.query({
                    filterquery: 'content_type:account AND object_id:' + id,
                    size: size
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
                        deal = $.extend(deal, {historyType: 'deal', color: 'blue', date: deal.modified});
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

            $scope.deleteNote = function(note) {
                if (confirm('Are you sure?')) {
                    NoteService.delete({
                        id:note.id
                    }, function() {  // On success
                        var index = $scope.history.indexOf(note);
                        $scope.history.splice(index, 1);
                    }, function(error) {  // On error
                        alert('something went wrong.')
                    });
                }
            };
        }
    ]);

    /**
     * Controller for update and new Account actions.
     */
    angular.module('app.accounts').controller('AccountUpsertController', [
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
    angular.module('app.accounts').controller('AccountDeleteController', [
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
})();
