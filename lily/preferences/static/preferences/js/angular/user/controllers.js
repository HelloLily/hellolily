(function(){
    'use strict';

    /**
     * PreferencesUserControllers is a container for all user preference related Controllers
     */
    angular.module('app.preferences.user', []);

    angular.module('app.preferences.user').config(userPreferencesStates);

    userPreferencesStates.$inject = ['$stateProvider'];
    function userPreferencesStates ($stateProvider) {
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
                    controller: 'PreferencesUserProfile',
                    controllerAs: 'vm'
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
                    controller: 'PreferencesUserAccount',
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'account'
            }
        });
    }

    /**
     * PreferencesUserProfile is a controller to show the user profile page.
     */
    angular.module('app.preferences.user').controller('PreferencesUserProfile', PreferencesUserProfile);
    function PreferencesUserProfile () {}

    /**
     * PreferencesUserAccount is a controller to show the user account page.
     */
    angular.module('app.preferences.user').controller('PreferencesUserAccount', PreferencesUserAccount);
    function PreferencesUserAccount () {}
})();
