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
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('PreferencesUserAccountController', PreferencesUserAccountController);

PreferencesUserAccountController.$inject = ['$state', 'HLForms', 'HLUtils', 'Settings', 'User', 'user'];
function PreferencesUserAccountController($state, HLForms, HLUtils, Settings, User, user) {
    const vm = this;

    Settings.page.setAllTitles('list', 'my account');

    vm.user = user;

    vm.saveUser = saveUser;
    vm.cancelAccountEditing = cancelAccountEditing;

    activate();

    //////

    function activate() {
    }

    function saveUser(form) {
        var formName = '[name="userForm"]';

        var args = {
            id: 'me',
            email: vm.user.email,
            password_confirmation: vm.user.password_confirmation,
        };

        if (vm.user.password) {
            // Because an empty string is sent otherwise, causing validation to fail.
            args.password = vm.user.password;
        }

        if (vm.user.password !== vm.user.password_check) {
            toastr.error('Your passwords don\'t match. Please fix and try again.', 'Attention!');
        } else {
            HLUtils.blockUI(formName, true);
            HLForms.clearErrors(form);

            User.patch(args).$promise.then(function() {
                toastr.success('I\'ve updated your account!', 'Done');
                $state.reload();
            }, function(response) {
                HLUtils.unblockUI(formName);
                HLForms.setErrors(form, response.data);

                toastr.error('Uh oh, there seems to be a problem', 'Oops!');
            });
        }
    }

    function cancelAccountEditing() {
        $state.reload();
    }
}
