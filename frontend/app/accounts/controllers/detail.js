/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.accounts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/detail.html',
                controller: AccountDetailController,
            },
        },
        ncyBreadcrumb: {
            label: '{{ account.name }}',
        },
        resolve: {
            currentAccount: ['Account', '$stateParams', function(Account, $stateParams) {
                var accountId = $stateParams.id;
                return Account.get({id: accountId}).$promise;
            }],
        },
    });
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['$scope', '$stateParams', 'Settings', 'Case', 'Contact', 'Deal', 'currentAccount'];
function AccountDetailController($scope, $stateParams, Settings, Case, Contact, Deal, currentAccount) {
    var id = $stateParams.id;

    $scope.account = currentAccount;
    Settings.page.setAllTitles('detail', currentAccount.name);

    $scope.caseList = Case.query({filterquery: 'account.id:' + id, sort: '-created', size: 100});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = Deal.query({filterquery: 'account.id:' + id, sort: '-created'});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });

    $scope.contactList = Contact.search({filterquery: 'accounts.id:' + id});
    $scope.contactList.$promise.then(function(results) {
        $scope.contactList = results.objects;
    });
}
