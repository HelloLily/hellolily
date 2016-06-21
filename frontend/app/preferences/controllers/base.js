angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences', {
        url: '/preferences',
        abstract: true,
        views: {
            '@': {
                templateUrl: 'preferences/controllers/base.html',
                controller: PreferencesBase,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Preferences',
        },
    });
}

angular.module('app.preferences').controller('PreferencesBase', PreferencesBase);

PreferencesBase.$inject = ['Settings'];
function PreferencesBase(Settings) {
    Settings.page.setAllTitles('custom', 'Preferences');
}
