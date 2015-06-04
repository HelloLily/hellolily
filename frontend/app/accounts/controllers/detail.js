/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {
    $stateProvider.state('base.accounts.detail', {
        url: '/{id:[0-9]{1,}}',
        views: {
            '@': {
                templateUrl: 'accounts/controllers/detail.html',
                controller: AccountDetailController
            }
        },
        ncyBreadcrumb: {
            label: '{{ account.name }}'
        },
        resolve: {
            account: ['AccountDetail', '$stateParams', function(AccountDetail, $stateParams) {
                var accountId = $stateParams.id;
                return AccountDetail.get({id: accountId}).$promise
            }]
        }
    })
}

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

    $scope.caseList = CaseDetail.query({filterquery: 'account:' + id});
    $scope.caseList.$promise.then(function(caseList) {
        $scope.caseList = caseList;
    });

    $scope.dealList = DealDetail.query({filterquery: 'account:' + id});
    $scope.dealList.$promise.then(function(dealList) {
        $scope.dealList = dealList;
    });

    $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + id});
    $scope.contactList.$promise.then(function(contactList) {
        $scope.contactList = contactList;
    });
}
