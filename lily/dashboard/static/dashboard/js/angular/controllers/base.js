(function() {
    'use strict';

    angular.module('app.dashboard').config(dashboardConfig);

    dashboardConfig.$inject = ['$stateProvider'];
    function dashboardConfig ($stateProvider) {
        $stateProvider.state('base.dashboard', {
            url: '/',
            views: {
                '@': {
                    templateUrl: 'dashboard/base.html',
                    controller: 'Dashboard',
                    controllerAs: 'vm'
                }
            },
            ncyBreadcrumb: {
                label: 'Dashboard'
            }
        });
    }

    angular.module('app.dashboard').controller('Dashboard', Dashboard);

    Dashboard.$inject = ['$scope'];
    function Dashboard ($scope) {
        $scope.conf.pageTitleBig = 'Dashboard';
        $scope.conf.pageTitleSmall = 'statistics and usage';
    }
})();
