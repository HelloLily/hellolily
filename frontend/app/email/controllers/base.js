angular.module('app.email').config(emailConfig);
emailConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
function emailConfig($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/email',  ['$state', 'Settings', function($state, Settings) {
        if (Settings.email.previousInbox) {
            // If we previously selected a certain inbox, redirect to that inbox.
            $state.transitionTo(Settings.email.previousInbox.state, Settings.email.previousInbox.params, false);
        } else {
            // Otherwise just go to the main inbox.
            $state.transitionTo('base.email.list', {labelId: 'INBOX'});
        }
    }]);

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
            'createDeal@base.email': {
                templateUrl: 'deals/controllers/form.html',
                controller: 'DealCreateUpdateController',
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

EmailBaseController.$inject = ['Settings'];
function EmailBaseController(Settings) {
    Settings.page.setTitle('custom', 'Email');
    Settings.page.header.setMain('custom', 'Email');
    Settings.page.header.setSub('email');

    activate();

    //////

    function activate() {
        Settings.email.resetEmailSettings();
    }
}

angular.module('app.email').controller('EmailShowAccountController', EmailShowAccountController);
EmailShowAccountController.$inject = ['$scope', 'AccountDetail', 'ContactDetail', 'Settings'];
function EmailShowAccountController($scope, AccountDetail, ContactDetail, Settings) {
    $scope.$watch('settings.email.sidebar.account', function(newValue, oldValue) {
        if (oldValue === 'showAccount' && newValue === 'checkAccount' && Settings.email.data.account.id) {
            activate();
        }
    }, true);

    activate();

    function activate() {
        AccountDetail.get({id: Settings.email.data.account.id}).$promise.then(function(account) {
            $scope.account = account;
            $scope.contactList = ContactDetail.query({filterquery: 'accounts.id:' + Settings.email.data.account.id});
            $scope.contactList.$promise.then(function(contactList) {
                $scope.contactList = contactList;
            });
        });
    }
}

angular.module('app.email').controller('EmailShowContactController', EmailShowContactController);
EmailShowContactController.$inject = ['$scope', 'ContactDetail', 'Settings'];
function EmailShowContactController($scope, ContactDetail, Settings) {
    $scope.$watch('settings.email.sidebar.contact', function(newValue, oldValue) {
        if (oldValue === 'showContact' && newValue === 'checkContact' && Settings.email.data.contact.id) {
            activate();
        }
    }, true);

    activate();

    function activate() {
        ContactDetail.get({id: Settings.email.data.contact.id}).$promise.then(function(contact) {
            $scope.contact = contact;
            $scope.height = 300;

            if ($scope.contact.accounts) {
                $scope.contact.accounts.forEach(function(account) {
                    var colleagueList = ContactDetail.query({filterquery: 'NOT(id:' + $scope.contact.id + ') AND accounts.id:' + account.id});
                    colleagueList.$promise.then(function(colleagues) {
                        account.colleagueList = colleagues;
                    });
                });

                if ($scope.contact.accounts.length >= 2) {
                    $scope.height = 91;
                }
            }
        });
    }
}
