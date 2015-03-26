/**
 * ContactsControllers is a container for all case related Controllers
 */
var UtilsControllers = angular.module('UtilsControllers', [
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
    $stateProvider.state('base.settings.email', {
        url: '/email',
        views: {
            '@base.settings': {
                templateUrl: 'utils/email.html',
                controller: 'UtilsEmailController'
            }
        },
        ncyBreadcrumb: {
            label: 'Email Settings'
        }
    });
}]);

/**
 * UtilsBaseController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('UtilsBaseController', [
    '$scope',
    function($scope) {
        $scope.showMoreText = 'Show more';
        $scope.conf.pageTitleBig = 'Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';
    }
]);

/**
 * UtilsEmailController is a controller to show the base of the settings page.
 */
UtilsControllers.controller('UtilsEmailController', [
    '$scope',
    function($scope) {
        $scope.showMoreText = 'Show more';
        $scope.conf.pageTitleBig = 'Email Settings';
        $scope.conf.pageTitleSmall = 'the devil is in the detail';
    }
]);

