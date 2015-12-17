angular.module('app.base').config(appConfig);

appConfig.$inject = ['$stateProvider'];
function appConfig($stateProvider) {
    $stateProvider.state('base', {
        abstract: true,
        controller: BaseController,
        ncyBreadcrumb: {
            label: 'Lily',
        },
    });
}

angular.module('app.base').controller('BaseController', BaseController);

BaseController.$inject = ['$scope', '$state', 'Settings', 'Notifications'];
function BaseController($scope, $state, Settings, Notifications) {
    $scope.settings = Settings;

    $scope.emailSettings = {
        sidebar: {
            account: null,
            contact: null,
            form: null,
            isVisible: false,
        },
        accountId: false,
        contactId: false,
    };

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
    }

    function _setPreviousState(event, toState, toParams, fromState, fromParams) {
        $scope.previousState = $state.href(fromState, fromParams);
        if ($scope.emailSettings.sidebar && fromState && fromState.name === 'base.email.detail') {
            $scope.emailSettings.sidebar = {
                account: null,
                contact: null,
                form: null,
                isVisible: false,
            };

            $scope.emailSettings.accountId = null;
            $scope.emailSettings.contactId = null;
            $scope.emailSettings.website = null;
            $scope.emailSettings.account = null;
            $scope.emailSettings.contact = null;

            $scope.$$phase || $scope.apply();
        }
    }
}
