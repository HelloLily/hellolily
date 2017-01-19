angular.module('app.preferences').config(moneybirdConfig);

moneybirdConfig.$inject = ['$stateProvider'];
function moneybirdConfig($stateProvider) {
    $stateProvider.state('base.preferences.admin.integrations.moneybird.auth', {
        url: '/auth',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/admin/integrations/moneybird.html',
            },
        },
        params: {
            type: 'Moneybird',
        },
    });
}
