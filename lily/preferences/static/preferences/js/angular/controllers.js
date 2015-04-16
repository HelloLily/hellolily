/**
 * PreferencesControllers is a container for all preference related Controllers
 */
var PreferencesControllers = angular.module('PreferencesControllers', []);

PreferencesControllers.config(['$stateProvider', function($stateProvider) {
    $stateProvider.state('base.preferences', {
        url: '/preferences',
        abstract: true,
        views: {
            '@': {
                templateUrl: 'preferences-base.html',
                controller: 'PreferencesBaseController'
            }
        },
        ncyBreadcrumb: {
            label: 'Preferences'
        }
    });
}]);

/**
 * PreferencesBaseController is a controller to show the base of the settings page.
 */
PreferencesControllers.controller('PreferencesBaseController', [
    '$scope',
    function($scope) {
        $scope.conf.pageTitleBig = 'Preferences';
        $scope.conf.pageTitleSmall = 'configure your mayhem';
    }
]);
