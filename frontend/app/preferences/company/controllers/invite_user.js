angular.module('app.preferences').config(preferencesInviteConfig);

preferencesInviteConfig.$inject = ['$stateProvider'];
function preferencesInviteConfig($stateProvider) {
    $stateProvider.state('base.preferences.company.users.inviteUser', {
        url: '/invite',
        views: {
            '@base.preferences': {
                templateUrl: 'invitation/invite',
                controller: PreferencesCompanyInviteUserController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'Invites',
        },
    });
}

angular.module('app.preferences').controller('PreferencesCompanyInviteUserController', PreferencesCompanyInviteUserController);

PreferencesCompanyInviteUserController.$inject = [];
function PreferencesCompanyInviteUserController() {
}
