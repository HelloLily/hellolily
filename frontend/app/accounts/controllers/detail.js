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
            account: ['Account', '$stateParams', function(Account, $stateParams) {
                var accountId = $stateParams.id;
                return Account.get({id: accountId}).$promise;
            }],
        },
    });
}

angular.module('app.accounts').controller('AccountDetailController', AccountDetailController);

AccountDetailController.$inject = ['$scope', '$stateParams', 'Settings', 'CaseDetail', 'ContactDetail', 'DealDetail', 'account'];
function AccountDetailController($scope, $stateParams, Settings, CaseDetail, ContactDetail, DealDetail, account) {
    /**
     * Details page with historylist and more detailed account information.
     */
    var id = $stateParams.id;

    $scope.account = account;
    Settings.page.setAllTitles('detail', account.name);

    $scope.caseList = CaseDetail.query({filterquery: 'account:' + id, sort: '-created', size: 100});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = DealDetail.query({filterquery: 'account:' + id, sort: '-created'});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });

    $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + id});
    $scope.contactList.$promise.then(function(contactList) {
        $scope.contactList = contactList;
    });
}
