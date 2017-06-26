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
        ncyBreadcrumb: {
            label: 'Invites',
        },
        resolve: {
            accountAdmin: ['Tenant', Tenant => {
                return Tenant.getAccountAdmin().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('InviteUsersController', InviteUsersController);

InviteUsersController.$inject = ['$state', 'HLForms', 'Settings', 'User', 'accountAdmin'];
function InviteUsersController($state, HLForms, Settings, User, accountAdmin) {
    let vm = this;

    vm.invites = [{
        first_name: '',
        email: '',
    }];
    vm.accountAdmin = accountAdmin.admin;

    vm.sendInvites = sendInvites;
    vm.addInvite = addInvite;

    Settings.page.setAllTitles('custom', 'Users');

    function sendInvites(form) {
        HLForms.blockUI();

        HLForms.clearErrors(form);

        let invites = vm.invites.filter(invite => {
            return !invite.is_deleted;
        });

        User.invite({invites}).$promise.then(() => {
            toastr.success('The invitations were sent successfully', 'Done');
            $state.go('base.preferences.company.users');
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

        toastr.error('Uh oh, there seems to be a problem', 'Oops!');
    }
}
