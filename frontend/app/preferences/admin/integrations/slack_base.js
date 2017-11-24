angular.module('app.preferences').config(slackConfig);

slackConfig.$inject = ['$stateProvider'];
function slackConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.slack', {
        url: '/slack',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/slack.html',
                controller: PreferencesSlackController,
                controllerAs: 'vm',
            },
        },
        params: {
            type: 'Slack',
        },
        resolve: {
            integration: ['Integration', Integration => Integration.get({type: 'slack'}).$promise],
        },
    });
}

angular.module('app.preferences').controller('PreferencesSlackController', PreferencesSlackController);

PreferencesSlackController.$inject = ['$http', '$state', '$window', 'Integration', 'integration'];
function PreferencesSlackController($http, $state, $window, Integration, integration) {
    const vm = this;
    const TYPE = 'slack';

    vm.hasIntegration = integration.has_integration;

    vm.authorize = authorize;
    vm.uninstall = uninstall;

    function authorize() {
        // Try to store the credentials so we can reuse them later.
        Integration.authenticate({type: TYPE}).$promise.then(response => {
            // Everything was ok, so go to the authorization page.
            $window.location.href = decodeURIComponent(response.url);
        });
    }

    function uninstall() {
        Integration.delete({type: TYPE}).$promise.then(response => {
            if (response.status_code === 204) {
                $state.reload();
            } else {
                toastr.error(messages.notifications.error, messages.notifications.errorTitle);
            }
        });
    }
}

