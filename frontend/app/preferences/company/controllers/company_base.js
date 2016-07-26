angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.company', {
        url: '/company',
        abstract: true,
        ncyBreadcrumb: {
            label: 'company',
        },
    });
}
