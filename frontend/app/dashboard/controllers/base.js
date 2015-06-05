angular.module('app.dashboard').config(dashboardConfig);

dashboardConfig.$inject = ['$stateProvider'];
function dashboardConfig ($stateProvider) {
    $stateProvider.state('base.dashboard', {
        url: '/',
        views: {
            '@': {
                templateUrl: 'dashboard/controllers/base.html',
                controller: DashboardController,
                controllerAs: 'vm'
            }
        },
        ncyBreadcrumb: {
            label: 'Dashboard'
        }
    });
}

angular.module('app.dashboard').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$scope'];
function DashboardController ($scope) {
    $scope.conf.pageTitleBig = 'Dashboard';
    $scope.conf.pageTitleSmall = 'statistics and usage';
}
