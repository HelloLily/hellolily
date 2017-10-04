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
    });
}

angular.module('app.preferences').controller('PreferencesSlackController', PreferencesSlackController);

PreferencesSlackController.$inject = ['$http', '$window'];
function PreferencesSlackController($http, $window) {
    const vm = this;

    vm.authorize = authorize;

    function authorize() {
        // Try to store the credentials so we can reuse them later.
        $http({
            method: 'POST',
            url: '/api/integrations/auth/slack',
        }).success(response => {
            // Everything was ok, so go to the authorization page.
            $window.location.href = decodeURIComponent(response.url);
        });
    }
}

