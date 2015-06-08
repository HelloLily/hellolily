angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig ($stateProvider) {
    $stateProvider.state('base.preferences.user', {
        url: '/user',
        abstract: true,
        ncyBreadcrumb: {
            label: 'user'
        }
    });
}
