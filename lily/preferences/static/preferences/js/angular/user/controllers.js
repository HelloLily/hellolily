/**
 * PreferencesUserControllers is a container for all user preference related Controllers
 */
var PreferencesUserControllers = angular.module('PreferencesUserControllers', [

]);

PreferencesEmailControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.preferences.user', {
        url: '/user',
        abstract: true,
        ncyBreadcrumb: {
            label: 'user'
        }
    });
    $stateProvider.state('base.preferences.user.profile', {
        url: '/profile',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/profile/',
                controller: 'PreferencesUserProfileController'
            }
        },
        ncyBreadcrumb: {
            label: 'profile'
        }
    });
    $stateProvider.state('base.preferences.user.account', {
        url: '/account',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/account/',
                controller: 'PreferencesUserAccountController'
            }
        },
        ncyBreadcrumb: {
            label: 'account'
        }
    });
}]);

/**
 * PreferencesUserProfileController is a controller to show the user profile page.
 */
PreferencesUserControllers.controller('PreferencesUserProfileController', [
    '$scope',

    function($scope) {}
]);

/**
 * PreferencesUserAccountController is a controller to show the user account page.
 */
PreferencesUserControllers.controller('PreferencesUserAccountController', [
    '$scope',

    function($scope) {}
]);
