angular.module('app.preferences').config(preferencesInviteConfig);

preferencesInviteConfig.$inject = ['$stateProvider'];
function preferencesInviteConfig($stateProvider) {
    $stateProvider.state('base.preferences.company.users.inviteUser', {
        url: '/invite',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/company/controllers/invite_users.html',
                controller: InviteUsersController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            accountAdmin: ['Tenant', Tenant => Tenant.getAccountAdmin().$promise],
        },
    });
}

angular.module('app.preferences').controller('InviteUsersController', InviteUsersController);

InviteUsersController.$inject = ['$state', 'HLForms', 'Settings', 'UserInvite', 'accountAdmin'];
function InviteUsersController($state, HLForms, Settings, UserInvite, accountAdmin) {
    const vm = this;

    vm.invites = [{
        first_name: '',
        email: '',
    }];
    vm.accountAdmin = accountAdmin.admin;

    vm.sendInvites = sendInvites;
    vm.addInvite = addInvite;

    function sendInvites(form) {
        HLForms.blockUI();

        HLForms.clearErrors(form);

        const invites = vm.invites.filter(invite => !invite.is_deleted);

        UserInvite.post({invites}).$promise.then(() => {
            toastr.success(messages.notifications.invitationSent, messages.notifications.successTitle);
            $state.go('base.preferences.company.users', {}, {reload: true});
        }, response => {
            _handleBadResponse(response, form);
        });
    }

    function addInvite() {
        vm.invites.push({
            first_name: '',
            email: '',
        });
    }

    function _handleBadResponse(response, form) {
        HLForms.setErrors(form, response.data);

        toastr.error(messages.notifications.error, messages.notifications.errorTitle);
    }
}
