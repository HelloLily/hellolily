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
        resolve: {
            user: ['User', User => User.me().$promise],
            myTeams: ['UserTeams', UserTeams => UserTeams.mine().$promise],
            teams: ['UserTeams', UserTeams => UserTeams.query().$promise],
        },
    });
}

angular.module('app.dashboard').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'LocalStorage', 'Settings', 'Tenant', 'myTeams', 'teams'];
function DashboardController($compile, $scope, $state, $templateCache, LocalStorage, Settings, Tenant, myTeams, teams) {
    const db = this;
    const storage = new LocalStorage($state.current.name + 'widgetInfo');

    db.widgetSettings = storage.get('', {});
    db.teams = teams.results;

    db.openWidgetSettingsModal = openWidgetSettingsModal;

    Settings.page.setAllTitles('custom', 'Dashboard');

    activate();

    //////

    function activate() {
        Tenant.query({}, tenant => {
            db.tenant = tenant;
        });

        db.teams.map(team => {
            team.selected = (myTeams.filter(myTeam => myTeam.id === team.id).length ? true : false);
        });
    }

    function openWidgetSettingsModal() {
        swal({
            title: messages.alerts.dashboard.title,
            html: $compile($templateCache.get('dashboard/controllers/widget_settings.html'))($scope),
            showCancelButton: true,
            showCloseButton: true,
        }).then(isConfirm => {
            if (isConfirm) {
                storage.put('', db.widgetSettings);
                $state.reload();
            }
        }).done();
    }
}
