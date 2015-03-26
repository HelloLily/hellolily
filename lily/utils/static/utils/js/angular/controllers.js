/**
 * ContactsControllers is a container for all case related Controllers
 */
var UtilsControllers = angular.module('UtilsControllers', [
    'EmailServices'
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
        url: '/emailaccount',
        views: {
            '@base.settings': {
                templateUrl: 'utils/emailaccount-list.html',
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
    '$scope',
    'EmailAccount',
    function($scope, EmailAccount) {
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
        }
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

