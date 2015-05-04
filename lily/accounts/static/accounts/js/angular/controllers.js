(function() {
    'use strict';

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

            $scope.account = AccountDetail.get({id: id});
            $scope.account.$promise.then(function(account) {
                $scope.account = account;
                $scope.conf.pageTitleBig = account.name;
                $scope.conf.pageTitleSmall = 'change is natural';
                HLSelect2.init();
            });

            CaseDetail.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
                $scope.numCases = total.total;
            });

            DealDetail.totalize({filterquery: 'archived:false AND account:' + id}).$promise.then(function(total) {
                $scope.numDeals = total.total;
            });

            ContactDetail.query({filterquery: 'accounts.id:' + id}).$promise.then(function(contacts) {
                $scope.workers = contacts;
            });
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
