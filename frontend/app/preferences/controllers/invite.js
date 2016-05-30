angular.module('app.preferences').config(preferencesInviteConfig);

preferencesInviteConfig.$inject = ['$stateProvider'];
function preferencesInviteConfig($stateProvider) {
    $stateProvider.state('base.preferences.invite', {
        url: '/invite',
        views: {
            '@base.preferences': {
                templateUrl: 'invitation/invite',
                controller: PreferencesInviteController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'account',
        },
    });
}

angular.module('app.preferences').controller('PreferencesInviteController', PreferencesInviteController);

PreferencesInviteController.$inject = [];
function PreferencesInviteController() {
}
