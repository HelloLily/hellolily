angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.account', {
        url: '/account',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/controllers/user_account.html',
                controller: PreferencesUserAccountController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'account',
        },
        resolve: {
            user: ['User', User => User.me().$promise],
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserAccountController', PreferencesUserAccountController);

PreferencesUserAccountController.$inject = ['$state', 'HLForms', 'HLUtils', 'User', 'user'];
function PreferencesUserAccountController($state, HLForms, HLUtils, User, user) {
    const vm = this;

    vm.user = user;

    vm.saveUser = saveUser;
    vm.cancelAccountEditing = cancelAccountEditing;

    activate();

    //////

    function activate() {
    }

    function saveUser(form) {
        const formName = '[name="userForm"]';

        const args = {
            id: 'me',
            email: vm.user.email,
            password_confirmation: vm.user.password_confirmation,
        };

        if (vm.user.password) {
            // Because an empty string is sent otherwise, causing validation to fail.
            args.password = vm.user.password;
        }

        if (vm.user.password !== vm.user.password_check) {
            toastr.error(messages.notifications.passwordMismatch, messages.notifications.passwordMismatchTitle);
        } else {
            HLUtils.blockUI(formName, true);
            HLForms.clearErrors(form);

            User.patch(args).$promise.then(() => {
                toastr.success(messages.notifications.userAccountUpdated, messages.notifications.successTitle);
                $state.reload();
            }, response => {
                HLUtils.unblockUI(formName);
                HLForms.setErrors(form, response.data);

                toastr.error(messages.notifications.error, messages.notifications.errorTitle);
            });
        }
    }

    function cancelAccountEditing() {
        $state.reload();
    }
}
