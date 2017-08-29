angular.module('app.preferences').config(pandaDocConfig);

pandaDocConfig.$inject = ['$stateProvider'];
function pandaDocConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.pandadoc.auth', {
        url: '/auth',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/pandadoc.html',
            },
        },
        params: {
            type: 'PandaDoc',
        },
    });
}
