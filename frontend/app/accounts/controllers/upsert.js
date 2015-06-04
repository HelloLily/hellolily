/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {
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
}

/**
 * Controller for update and new Account actions.
 */
angular.module('app.accounts').controller('AccountUpsertController', AccountUpsertController);

AccountUpsertController.$inject = ['$scope', '$stateParams', 'AccountDetail'];
function AccountUpsertController ($scope, $stateParams, AccountDetail) {
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
