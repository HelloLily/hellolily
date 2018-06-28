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

BaseController.$inject = ['$scope', '$state', '$http', '$location', 'AppHash', 'Settings', 'HLShortcuts', 'User'];
function BaseController($scope, $state, $http, $location, AppHash, Settings, HLShortcuts, User) {
    // Make sure the settings are available everywhere.
    $scope.settings = Settings;

    $scope.loadNotifications = loadNotifications;

    activate();

    //////////

    function activate() {
        User.me().$promise.then(function(response) {
            $scope.settings.currentUser = response;
        });

        $scope.$on('$stateChangeStart', function() {
            new window.Intercom('update', {email: currentUser.email});
        });

        $scope.$on('$stateChangeSuccess', _setPreviousState);
        $scope.$on('$viewContentLoaded', _contentLoadedActions);

        $scope.$on('$stateChangeError', _handleResolveErrors);

        $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams) {
            const path = $location.path();
            let queryString = '';
            let referrer = '';

            // Check if there is a query string?
            if (path.indexOf('?') !== -1) {
                queryString = path.substring(path.indexOf('?'), path.length);
            }

            // Check if there is a referer?
            if (fromState.name) {
                referrer = $location.protocol() + '://' + $location.host() + '/#' + fromState.url;
            }

            // Track a page event in Segment each time you change states.
            analytics.page({
                path: path,
                referrer: referrer,
                search: queryString,
                url: $location.absUrl(),
            });

            // Identify a user in Segment when he navigates to a different state.
            let currentUser = $scope.settings.currentUser;
            if (currentUser) {
                analytics.identify(currentUser.id, {
                    name: currentUser.full_name,
                    email: currentUser.email,
                    tenant_id: currentUser.tenant.id,
                    tenant_name: currentUser.tenant.name,
                    plan_tier: currentUser.tenant.billing ? currentUser.tenant.billing.plan.tier : '',
                    is_free_plan: currentUser.tenant.billing ? currentUser.tenant.billing.is_free_plan : '',
                });
            }
        });
    }

    function loadNotifications() {
        $http.get('/api/utils/notifications/').then(function(notifications) {  // On success
            angular.forEach(notifications.data, function(message) {
                toastr[message.level](message.message);
            });
        }, function(error) {  // On error
            if (error.status === 403) {
                toastr.error(error, 'You\'ve been logged out, please reload the page.');
            } else {
                toastr.error(error, 'Couldn\'t load notifications');
            }
        });
    }

    function _setPreviousState(event, toState, toParams, fromState, fromParams) {
        var previousInbox;

        $scope.previousState = $state.href(fromState, fromParams);
        Settings.page.previousState = {state: fromState, params: fromParams};

        if (['base.email.list', 'base.email.accountList', 'base.email.accountAllList'].includes(fromState.name)) {
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

        // For some reason we need to do two update calls to display messages
        // when they should.
        new window.Intercom('update', {email: currentUser.email});
    }

    function _contentLoadedActions() {
        AppHash.get().$promise.then(response => {
            // App hash is set, so compare with the response.
            if (window.appHash && window.appHash !== response.app_hash) {
                // Reload the page so we get new static files.
                window.location.reload(true);
            } else {
                window.appHash = response.app_hash;
            }
        });

        Metronic.unblockUI();
        Metronic.initComponents(); // init core components
        HLSelect2.init();
        HLFormsets.init();
        autosize($('textarea'));

        $scope.loadNotifications();
        $scope.toolbar = Settings.page.toolbar.data;
    }

    function _handleResolveErrors(event, toState, toParams, fromState, fromParams, error) {
        switch (error.status) {
            case 404:
                $state.go('base.404');
                break;
            case 403:
                window.location.href = '/';
                break;
            default:
                // With JS errors, error isn't an object, but still the default case gets called.
                $state.go('base.500');
        }
    }
}
