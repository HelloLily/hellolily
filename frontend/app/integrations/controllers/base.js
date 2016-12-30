angular.module('app.integrations').config(integrationsBaseConfig);

integrationsBaseConfig.$inject = ['$stateProvider'];
function integrationsBaseConfig($stateProvider) {
    $stateProvider.state('base.integrations', {
        abstract: true,
    });

    $stateProvider.state('base.integrations.pandadoc', {
        url: '/pandadoc',
    });

    $stateProvider.state('base.integrations.moneybird', {
        url: '/moneybird',
    });
}
