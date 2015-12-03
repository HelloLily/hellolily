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

DashboardController.$inject = ['$uibModal', '$state', 'Settings'];
function DashboardController($uibModal, $state, Settings) {
    var db = this;

    db.openWidgetSettingsModal = openWidgetSettingsModal;

    Settings.page.setTitle('custom', 'Dashboard');
    Settings.page.header.setMain('custom', 'Dashboard');
    Settings.page.header.setSub('custom', 'statistics and usage');

    ////////////

    function openWidgetSettingsModal() {
        var modalInstance = $uibModal.open({
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
