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
            },
            resolve: {
                AccountDetail: 'AccountDetail',
                account: function(AccountDetail, $stateParams) {
                    var accountId = $stateParams.id;
                    return AccountDetail.get({id: accountId}).$promise
                }
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
            }
        });

    }]);

    angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

    AccountDetailController.$inject = ['$scope', '$stateParams', 'CaseDetail', 'ContactDetail', 'DealDetail', 'account'];
    function AccountDetailController($scope, $stateParams, CaseDetail, ContactDetail, DealDetail, account) {
        /**
         * Details page with historylist and more detailed account information.
         */
        var id = $stateParams.id;

        $scope.account = account;
        $scope.conf.pageTitleBig = account.name;
        $scope.conf.pageTitleSmall = 'change is natural';

        $scope.caseList = CaseDetail.query({filterquery: 'archived:false AND account:' + id});
        $scope.caseList.$promise.then(function(caseList) {
            $scope.caseList = caseList;
        });

        $scope.dealList = DealDetail.query({filterquery: 'archived:false AND account:' + id});
        $scope.dealList.$promise.then(function(dealList) {
            $scope.dealList = dealList;
        });

        $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + id});
        $scope.contactList.$promise.then(function(contactList) {
            $scope.contactList = contactList;
        });
    }

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
