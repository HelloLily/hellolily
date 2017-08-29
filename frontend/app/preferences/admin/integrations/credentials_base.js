angular.module('app.preferences').config(credentialsConfig);

credentialsConfig.$inject = ['$stateProvider'];
function credentialsConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.pandadoc', {
        url: '/pandadoc',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/pandadoc_base.html',
            },
        },
        params: {
            type: 'PandaDoc',
        },
    });

    $stateProvider.state('base.preferences.admin.integrations.moneybird', {
        url: '/moneybird',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/moneybird_base.html',
            },
        },
    });
}
