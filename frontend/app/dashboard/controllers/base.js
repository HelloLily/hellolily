angular.module('app.dashboard').config(dashboardConfig);

dashboardConfig.$inject = ['$stateProvider'];
function dashboardConfig($stateProvider) {
    $stateProvider.state('base.dashboard', {
        url: '/',
        views: {
            '@': {
                templateUrl: 'dashboard/controllers/base.html',
                controller: DashboardController,
                controllerAs: 'db',
            },
        },
        ncyBreadcrumb: {
            label: 'Dashboard',
        },
    });
}

angular.module('app.dashboard').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$modal', '$scope', '$state'];
function DashboardController($modal, $scope, $state) {
    var db = this;

    db.openWidgetSettingsModal = openWidgetSettingsModal;

    $scope.conf.pageTitleBig = 'Dashboard';
    $scope.conf.pageTitleSmall = 'statistics and usage';

    ////////////

    function openWidgetSettingsModal() {
        var modalInstance = $modal.open({
            templateUrl: 'dashboard/controllers/widget_settings.html',
            controller: 'WidgetSettingsModal',
            controllerAs: 'vm',
            size: 'md',
        });

        modalInstance.result.then(function() {
            $state.reload();
        });
    }
}
