angular.module('app.preferences').config(integrationsConfig);

integrationsConfig.$inject = ['$stateProvider'];
function integrationsConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations', {
        url: '/integrations',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/integrations.html',
                controller: PreferencesIntegrationsController,
                controllerAs: 'vm',
            },
        },
    });
}

angular.module('app.preferences').controller('PreferencesIntegrationsController', PreferencesIntegrationsController);

PreferencesIntegrationsController.$inject = ['$scope'];
function PreferencesIntegrationsController($scope) {
}
