angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.profile', {
        url: '/profile',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/profile/',
                controller: PreferencesUserProfileController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'profile',
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserProfile', PreferencesUserProfileController);
function PreferencesUserProfileController() {}
