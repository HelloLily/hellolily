angular.module('app.dashboard').config(dashboardConfig);

dashboardConfig.$inject = ['$stateProvider', '$urlRouterProvider'];
function dashboardConfig($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.when('/',  ['$state', 'User', function($state, User) {
        User.me().$promise.then(function(user) {
            if (user.info !== null && !user.info.email_account_status) {
                // User has logged in for the first time, so redirect to the email account setup.
                $state.go('base.preferences.emailaccounts.setup');
            } else {
                $state.go('base.dashboard');
            }
        });
    }]);

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
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.dashboard').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'LocalStorage', 'Settings', 'Tenant'];
function DashboardController($compile, $scope, $state, $templateCache, LocalStorage, Settings, Tenant) {
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
