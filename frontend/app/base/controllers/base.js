angular.module('app.base').config(appConfig);

appConfig.$inject = ['$stateProvider'];
function appConfig($stateProvider) {
    $stateProvider.state('base', {
        controller: BaseController,
        ncyBreadcrumb: {
            label: 'Lily',
        },
    });
}

angular.module('app.base').controller('BaseController', BaseController);

BaseController.$inject = ['$scope', '$state', 'Settings', 'Notifications', 'HLShortcuts'];
function BaseController($scope, $state, Settings, Notifications, HLShortcuts) {
    // Make sure the settings are available everywhere.
    $scope.settings = Settings;

    $scope.loadNotifications = loadNotifications;

    activate();

    //////////

    function activate() {
        $scope.$on('$stateChangeSuccess', _setPreviousState);
        $scope.$on('$viewContentLoaded', _contentLoadedActions);
    }

    function loadNotifications() {
        Notifications.query(function(notifications) {  // On success
            angular.forEach(notifications, function(message) {
                toastr[message.level](message.message);
            });
        }, function(error) {  // On error
            toastr.error(error, 'Couldn\'t load notifications');
        });
    }

    function _contentLoadedActions() {
        Metronic.unblockUI();
        Metronic.initComponents(); // init core components
        HLSelect2.init();
        HLFormsets.init();
        HLShowAndHide.init();
        autosize($('textarea'));

        $scope.loadNotifications();
        $scope.toolbar = Settings.page.toolbar.data;

        new window.Intercom('update');
    }

    function _setPreviousState(event, toState, toParams, fromState, fromParams) {
        var previousInbox;

        $scope.previousState = $state.href(fromState, fromParams);

        if (fromState.name === 'base.email.list' || fromState.name === 'base.email.accountList') {
            previousInbox = {
                state: fromState.name,
                params: fromParams,
            };

            Settings.email.setPreviousInbox(previousInbox);
        }

        if (Settings.email.sidebar && fromState && fromState.name === 'base.email.detail') {
            Settings.email.resetEmailSettings();

            $scope.$$phase || $scope.apply();
        }

        Settings.page.toolbar.data = null;
    }
}
