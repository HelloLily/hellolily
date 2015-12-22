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
                controllerAs: 'vm',
            },
            'labelList@base.email': {
                templateUrl: 'email/controllers/label_list.html',
                controller: 'LabelListController',
                controllerAs: 'vm',
            },
            'createAccount@base.email': {
                templateUrl: 'accounts/controllers/form.html',
                controller: 'AccountCreateController',
                controllerAs: 'vm',
            },
            'showAccount@base.email': {
                controller: EmailShowAccountController,
            },
            'createContact@base.email': {
                templateUrl: 'contacts/controllers/form.html',
                controller: 'ContactCreateUpdateController',
                controllerAs: 'vm',
            },
            'showContact@base.email': {
                controller: EmailShowContactController,
            },
            'createCase@base.email': {
                templateUrl: 'cases/controllers/form.html',
                controller: 'CaseCreateUpdateController',
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Email',
        },
        resolve: {
            primaryEmailAccountId: ['$q', 'User', function($q, User) {
                var deferred = $q.defer();
                User.me(null, function(data) {
                    deferred.resolve(data.primary_email_account);
                });
                return deferred.promise;
            }],
        },
    });
}

angular.module('app.email').controller('EmailBaseController', EmailBaseController);

EmailBaseController.$inject = ['$scope', '$state', 'Settings'];
function EmailBaseController($scope, $state, Settings) {
    Settings.page.setTitle('custom', 'Email');
    Settings.page.header.setMain('custom', 'Email');
    Settings.page.header.setSub('email');

    console.log($scope);
    console.log($state);

    activate();

    //////

    function activate() {
        $scope.emailSettings.sidebar = {
            account: null,
            contact: null,
            form: null,
            isVisible: false,
        };
    }
}

angular.module('app.email').controller('EmailShowAccountController', EmailShowAccountController);
EmailShowAccountController.$inject = ['$scope', 'AccountDetail', 'ContactDetail'];
function EmailShowAccountController($scope, AccountDetail, ContactDetail) {
    $scope.$watch('emailSettings.sidebar.account', function(newValue, oldValue) {
        if (oldValue === 'showAccount' && newValue === 'checkAccount' && $scope.emailSettings.accountId) {
            activate();
        }
    }, true);

    activate();

    function activate() {
        AccountDetail.get({id: $scope.emailSettings.accountId}).$promise.then(function(account) {
            $scope.account = account;
            $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + $scope.emailSettings.accountId});
            $scope.contactList.$promise.then(function(contactList) {
                $scope.contactList = contactList;
            });
        });
    }
}

angular.module('app.email').controller('EmailShowContactController', EmailShowContactController);
EmailShowContactController.$inject = ['$scope', 'ContactDetail'];
function EmailShowContactController($scope, ContactDetail) {
    $scope.$watch('emailSettings.sidebar.contact', function(newValue, oldValue) {
        if (oldValue === 'showContact' && newValue === 'checkContact' && $scope.emailSettings.contactId) {
            activate();
        }
    }, true);

    activate();

    function activate() {
        ContactDetail.get({id: $scope.emailSettings.contactId}).$promise.then(function(contact) {
            $scope.contact = contact;

            if ($scope.contact.accounts) {
                $scope.contact.accounts.forEach(function(account) {
                    var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + $scope.contact.id + ') AND accounts.id:' + account.id});
                    colleagueList.$promise.then(function(colleagues) {
                        account.colleagueList = colleagues;
                    });
                });
            }
        });
    }
}
