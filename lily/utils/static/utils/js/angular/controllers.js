/**
 * ContactsControllers is a container for all case related Controllers
 */
var UtilsControllers = angular.module('UtilsControllers', [
    'ui.bootstrap',
    'ui.slimscroll',
    'EmailServices',
    'LilyServices',
    'UserFilters',
    'UserServices'
]);

UtilsControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.settings', {
        url: '/settings',
        views: {
            '@': {
                templateUrl: 'utils/base.html',
                controller: 'UtilsBaseController'
            }
        },
        ncyBreadcrumb: {
            label: 'Settings'
        }
    });
    $stateProvider.state('base.settings.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.settings': {
                templateUrl: 'utils/emailaccounts-list.html',
                controller: 'UtilsEmailAccountListController'
            }
        },
        ncyBreadcrumb: {
            label: 'EmailAccount Settings'
        }
    });
    $stateProvider.state('base.settings.emailaccounts.edit', {
        url: '/edit/{id:int}',
        views: {
            '@base.settings': {
                templateUrl: function (elem, attr) {
                    return 'messaging/email/accounts/update/' + elem.id;
                },
                controller: 'UtilsEmailAccountEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit EmailAccount'
        }
    });
    $stateProvider.state('base.settings.emailtemplates', {
        url: '/emailtemplates',
        views: {
            '@base.settings': {
                templateUrl: 'utils/emailtemplates-list.html',
                controller: 'UtilsEmailTemplatesListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email templates'
        }
    });
    $stateProvider.state('base.settings.emailtemplates.create', {
        url: '/create',
        views: {
            '@base.settings': {
                templateUrl: '/messaging/email/templates/create/',
                controller: 'UtilsEmailTemplatesCreateController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email template edit'
        }
    });
    $stateProvider.state('base.settings.emailtemplates.edit', {
        url: '/edit/{id:int}',
        views: {
            '@base.settings': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templates/update/' + elem.id +'/';
                },
                controller: 'UtilsEmailTemplatesEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email template create'
        }
    });
}]);

/**
 * UtilsBaseController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('UtilsBaseController', [
    '$scope',
    function($scope) {
        $scope.conf.pageTitleBig = 'Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';
    }
]);

/**
 * UtilsEmailAccountListController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('UtilsEmailAccountListController', [
    '$modal',
    '$scope',
    'EmailAccount',
    function($modal, $scope, EmailAccount) {
        $scope.conf.pageTitleBig = 'EmailAccount Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';

        // Get relevant accounts
        var loadAccounts = function() {
            // Accounts owned
            EmailAccount.query({owner: currentUser.id}, function(data) {
               $scope.ownedAccounts = data;
            });

            // Accounts shared with user
            EmailAccount.query({shared_with_users__id: currentUser.id}, function(data) {
               $scope.sharedAccounts = data;
            });

            // Accounts public
            EmailAccount.query({public: "True"}, function(data) {
               $scope.publicAccounts = data;
            });
        };
        // Initial load
        loadAccounts();

        $scope.deleteAccount = function (accountId) {
            if (confirm('sure to delete?')) {
                EmailAccount.delete({id: accountId}, function() {
                    // Reload accounts
                    loadAccounts();
                });
            }
        };

        $scope.openShareAccountModal = function (emailAccount) {
            var modalInstance = $modal.open({
                templateUrl: 'utils/emailaccount-share.html',
                controller: 'EmailAccountShareModalController',
                size: 'lg',
                resolve: {
                        currentAccount: function() {
                            return emailAccount;
                        }
                }
            });

            modalInstance.result.then(function () {
                loadAccounts();
            }, function() {
                loadAccounts();
            });
        };
    }
]);

/**
 * UtilsEmailAccountEditController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('UtilsEmailAccountEditController', [
    '$scope',
    function($scope) {
        $scope.conf.pageTitleBig = 'EmailAccount Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';
    }
]);

/**
 * UtilsEmailTemplatesListController is a controller to show the email template list.
 */
UtilsControllers.controller('UtilsEmailTemplatesListController', [
    '$scope',
    'EmailTemplate',
    function($scope, EmailTemplate) {
        $scope.conf.pageTitleBig = 'EmailTemplate Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';

        EmailTemplate.query({}, function(data) {
            $scope.emailTemplates = data;
        });

        $scope.makeDefault = function(templateId) {
            console.log(templateId);
        }
    }
]);

/**
 * UtilsEmailTemplatesEditController is a controller to show edit an email template.
 */
UtilsControllers.controller('UtilsEmailTemplatesCreateController', [
    // TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
    function () {
        HLInbox.init();
        HLInbox.initWysihtml5();
        HLEmailTemplates.init({
            parseEmailTemplateUrl: '',
            openVariable: '[[',
            closeVariable: ']]'
        });
    }
]);

/**
 * UtilsEmailTemplatesEditController is a controller to show edit an email template.
 */
UtilsControllers.controller('UtilsEmailTemplatesEditController', [
    // TODO: LILY-XXX: Try to change the openVariable and closeVariable to curly braces, so it's consistent with other templating engines
    function () {
        HLInbox.init();
        HLInbox.initWysihtml5();
        HLEmailTemplates.init({
            parseEmailTemplateUrl: '',
            openVariable: '[[',
            closeVariable: ']]'
        });
    }
]);

/**
 * EmailAccountShareModalController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('EmailAccountShareModalController', [
    '$modalInstance',
    '$scope',
    'EmailAccount',
    'User',
    'currentAccount',
    function($modalInstance, $scope, EmailAccount, User, currentAccount) {
        $scope.currentAccount = currentAccount;

        // Get all users to display in a list
        User.query({}, function(data) {
            $scope.users = [];
            // Check if user has the emailaccount already shared
            angular.forEach(data, function(user) {
                if ($scope.currentAccount.shared_with_users.indexOf(user.id) !== -1) {
                    user.sharedWith = true;
                }
                $scope.users.push(user);
            });
        });

        $scope.ok = function () {
            // Save updated account information
            if ($scope.currentAccount.public) {
                EmailAccount.update({id: $scope.currentAccount.id}, $scope.currentAccount, function() {
                    $modalInstance.close();
                });
            } else {
                // Get ids of the users to share with
                var shared_with_users = [];
                angular.forEach($scope.users, function(user) {
                    if(user.sharedWith) {
                        shared_with_users.push(user.id);
                    }
                });
                // Push ids to api
                EmailAccount.shareWith({id: $scope.currentAccount.id}, {shared_with_users: shared_with_users}, function() {
                    $modalInstance.close();
                });
            }
        };

        // Lets not change anything
        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };
    }
]);
