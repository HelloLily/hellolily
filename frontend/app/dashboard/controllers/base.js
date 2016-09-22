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

DashboardController.$inject = ['$compile', '$scope', '$state', '$templateCache', '$timeout', 'LocalStorage',
    'Settings', 'Tenant'];
function DashboardController($compile, $scope, $state, $templateCache, $timeout, LocalStorage,
                             Settings, Tenant) {
    var db = this;
    var storage = new LocalStorage($state.current.name + 'widgetInfo');

    db.widgetSettings = storage.get('', {});

    db.openWidgetSettingsModal = openWidgetSettingsModal;

    Settings.page.setAllTitles('custom', 'Dashboard');

    activate();

    //////

    function activate() {
        Tenant.query({}, function(tenant) {
            db.tenant = tenant;
        });
    }

    function openWidgetSettingsModal() {
        swal({
            title: messages.alerts.dashboard.title,
            html: $compile($templateCache.get('dashboard/controllers/widget_settings.html'))($scope),
            showCancelButton: true,
            showCloseButton: true,
        }).then(function(isConfirm) {
            if (isConfirm) {
                storage.put('', db.widgetSettings);
                $state.reload();
            }
        }).done();
    }
}
