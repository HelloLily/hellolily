angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.account', {
        url: '/account',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/account/',
                controller: PreferencesUserAccountController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'account',
        },
    });
}

/**
 * PreferencesUserAccount is a controller to show the user account page.
 */
angular.module('app.preferences').controller('PreferencesUserAccountController', PreferencesUserAccountController);

PreferencesUserAccountController.$inject = ['$scope'];
function PreferencesUserAccountController($scope) {
    $scope.$on('$viewContentLoaded', function() {
        djangoPasswordStrength.initListeners();
    });
}
