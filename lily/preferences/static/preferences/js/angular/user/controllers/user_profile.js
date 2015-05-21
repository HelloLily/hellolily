(function(){
    'use strict';

    angular.module('app.preferences.user').config(userPreferencesStates);

    userPreferencesStates.$inject = ['$stateProvider'];
    function userPreferencesStates ($stateProvider) {
        $stateProvider.state('base.preferences.user.profile', {
            url: '/profile',
            views: {
                '@base.preferences': {
                    templateUrl: 'preferences/user/profile/',
                    controller: PreferencesUserProfile,
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'profile'
            }
        });
    }

    /**
     * PreferencesUserProfile is a controller to show the user profile page.
     */
    angular.module('app.preferences.user').controller('PreferencesUserProfile', PreferencesUserProfile);
    function PreferencesUserProfile () {}
})();
