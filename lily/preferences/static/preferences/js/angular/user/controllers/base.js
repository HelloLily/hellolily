(function(){
    'use strict';

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
    }
})();
