(function() {
    'use strict';

    angular.module('app.preferences').config(preferencesStates);

    preferencesStates.$inject = ['$stateProvider'];
    function preferencesStates ($stateProvider) {
        $stateProvider.state('base.preferences', {
            url: '/preferences',
            abstract: true,
            views: {
                '@': {
                    templateUrl: 'preferences-base.html',
                    controller: 'PreferencesBase',
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'Preferences'
            }
        });
    }

    /**
     * PreferencesBase is a controller to show the base of the settings page.
     */
    angular.module('app.preferences').controller('PreferencesBase', PreferencesBase);

    PreferencesBase.$inject = ['$scope'];
    function PreferencesBase ($scope) {
        $scope.conf.pageTitleBig = 'Preferences';
        $scope.conf.pageTitleSmall = 'configure your mayhem';
    }
})();
