/**
 * ContactsControllers is a container for all case related Controllers
 */
var PreferencesEmailControllers = angular.module('PreferencesEmailControllers', [
    'ui.bootstrap',
    'ui.slimscroll',
    'EmailServices',
    'LilyServices',
    'UserFilters',
    'UserServices'
]);

PreferencesEmailControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts', {
        url: '/emailaccounts',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/emailaccounts-list.html',
                controller: 'PreferencesEmailAccountListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email Accounts'
        }
    });
    $stateProvider.state('base.preferences.emailaccounts.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function (elem, attr) {
                    return 'messaging/email/accounts/update/' + elem.id;
                },
                controller: 'PreferencesEmailAccountEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Edit EmailAccount'
        }
    });
    $stateProvider.state('base.preferences.emailtemplates', {
        url: '/emailtemplates',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/emailtemplates-list.html',
                controller: 'PreferencesEmailTemplatesListController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email templates'
        }
    });
    $stateProvider.state('base.preferences.emailtemplates.create', {
        url: '/create',
        views: {
            '@base.preferences': {
                templateUrl: '/messaging/email/templates/create/',
                controller: 'PreferencesEmailTemplatesCreateController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email template edit'
        }
    });
    $stateProvider.state('base.preferences.emailtemplates.edit', {
        url: '/edit/{id:[0-9]{1,}}',
        views: {
            '@base.preferences': {
                templateUrl: function(elem, attr) {
                    return '/messaging/email/templates/update/' + elem.id +'/';
                },
                controller: 'PreferencesEmailTemplatesEditController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email template create'
        }
    });
}]);

/**
 * PreferencesEmailAccountListController is a controller to show the base of the settings page.
 */
PreferencesEmailControllers.controller('PreferencesEmailAccountListController', [
    '$modal',
    '$scope',
    'EmailAccount',
    function($modal, $scope, EmailAccount) {
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
                templateUrl: 'preferences/emailaccount-share.html',
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
 * PreferencesEmailAccountEditController is a controller to show the base of the settings page.
 */
PreferencesEmailControllers.controller('PreferencesEmailAccountEditController', [
    '$scope',
    function($scope) {}
]);

/**
 * PreferencesEmailTemplatesListController is a controller to show the email template list.
 */
PreferencesEmailControllers.controller('PreferencesEmailTemplatesListController', [
    '$modal',
    '$scope',
    'EmailTemplate',
    function($modal, $scope, EmailTemplate) {
        //$scope.conf.pageTitleBig = 'EmailTemplate settings';
        //$scope.conf.pageTitleSmall = 'the devil is in the detail';

        EmailTemplate.query({}, function(data) {
            $scope.emailTemplates = data;
        });

        $scope.makeDefault = function(emailTemplate) {
            // TODO: LILY-756: Make this controller more Angular
            var modalInstance = $modal.open({
                templateUrl: '/messaging/email/templates/set-default/' + emailTemplate.id + '/',
                controller: 'PreferencesSetTemplateDefaultModalController',
                size: 'lg',
                resolve: {
                    emailTemplate: function () {
                        return emailTemplate;
                    }
                }
            });

            modalInstance.result.then(function () {
                $state.go($state.current, {}, {reload: false});
            }, function () {
            });
        };

        $scope.deleteEmailTemplate = function(emailtemplate) {
            if (confirm('Are you sure?')) {
                EmailTemplate.delete({
                    id: emailtemplate.id
                }, function() {  // On success
                    var index = $scope.emailTemplates.indexOf(emailtemplate);
                    $scope.emailTemplates.splice(index, 1);
                }, function(error) {  // On error
                    alert('something went wrong.')
                })
            }
        };
    }
]);

PreferencesEmailControllers.controller('PreferencesSetTemplateDefaultModalController', [
    '$http',
    '$modalInstance',
    '$scope',
    'emailTemplate',
    function($http, $modalInstance, $scope, emailTemplate) {
        $scope.emailTemplate = emailTemplate;

        $scope.ok = function () {
            $http({
                url: '/messaging/email/templates/set-default/' + $scope.emailTemplate.id + '/',
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                data: $.param({id: $scope.emailTemplate.id})
            }).success(function() {
                $modalInstance.close($scope.emailTemplate);
            });
        };

        // Lets not change anything
        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
        };
    }
]);

/**
 * PreferencesEmailTemplatesEditController is a controller to show edit an email template.
 */
PreferencesEmailControllers.controller('PreferencesEmailTemplatesCreateController', [
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
 * PreferencesEmailTemplatesEditController is a controller to show edit an email template.
 */
PreferencesEmailControllers.controller('PreferencesEmailTemplatesEditController', [
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
PreferencesEmailControllers.controller('EmailAccountShareModalController', [
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
