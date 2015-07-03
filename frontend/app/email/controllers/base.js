angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
function emailConfig($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/email', '/email/all/INBOX');
    $stateProvider.state('base.email', {
        url: '/email',
        views: {
            '@': {
                templateUrl: 'email/controllers/base.html',
                controller: EmailBaseController,
                controllerAs: 'vm'
            },
            'labelList@base.email': {
                templateUrl: 'email/controllers/label_list.html',
                controller: 'LabelListController',
                controllerAs: 'vm'
            },
            'createaccount@base.email': {
                templateUrl: 'accounts/controllers/form.html',
                controller: 'AccountCreateController',
                controllerAs: 'vm'
            },
            'showaccount@base.email': {
                controller: EmailShowAccountController
            }
        },
        ncyBreadcrumb: {
            label: 'Email'
        },
        resolve: {
            primaryEmailAccountId: ['$q', 'User', function($q, User) {
                var deferred = $q.defer();
                User.me(null, function(data) {
                    deferred.resolve(data.primary_email_account);
                });
                return deferred.promise;
            }]
        }
    });
}

angular.module('app.email').controller('EmailBaseController', EmailBaseController);

EmailBaseController.$inject = ['$scope'];
function EmailBaseController ($scope) {
    $scope.conf.pageTitleBig = 'Email';
    $scope.conf.pageTitleSmall = 'sending love through the world!';

    activate();

    //////

    function activate(){
        $scope.emailSettings.sideBar = false;
    }
}

angular.module('app.email').controller('EmailShowAccountController', EmailShowAccountController);

EmailShowAccountController.$inject = ['$scope', 'AccountDetail', 'ContactDetail'];
function EmailShowAccountController ($scope, AccountDetail, ContactDetail) {
    $scope.$watch('emailSettings.sideBar', function(newValue, oldValue){
        if(oldValue == 'showAccount' && newValue == 'checkAccount' && $scope.emailSettings.accountId){
            activate();
        }
    }, true);

    activate();

    function activate() {
        AccountDetail.get({id: $scope.emailSettings.accountId}).$promise.then(function (account) {
            $scope.account = account;
            $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + $scope.emailSettings.accountId});
            $scope.contactList.$promise.then(function (contactList) {
                $scope.contactList = contactList;
            });
        });
    }
}
