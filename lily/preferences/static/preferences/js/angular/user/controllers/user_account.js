(function(){
    'use strict';

    angular.module('app.preferences.user').config(userPreferencesStates);

    userPreferencesStates.$inject = ['$stateProvider'];
    function userPreferencesStates ($stateProvider) {
        $stateProvider.state('base.preferences.user.account', {
            url: '/account',
            views: {
                '@base.preferences': {
                    templateUrl: 'preferences/user/account/',
                    controller: PreferencesUserAccount,
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'account'
            }
        });
    }

    /**
     * PreferencesUserAccount is a controller to show the user account page.
     */
    angular.module('app.preferences.user').controller('PreferencesUserAccount', PreferencesUserAccount);
    function PreferencesUserAccount () {}
})();
