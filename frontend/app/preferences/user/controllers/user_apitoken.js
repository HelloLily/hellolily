angular.module('app.preferences').config(preferencesConfig);

preferencesConfig.$inject = ['$stateProvider'];
function preferencesConfig($stateProvider) {
    $stateProvider.state('base.preferences.user.token', {
        url: '/token',
        views: {
            '@base.preferences': {
                templateUrl: 'preferences/user/controllers/user_apitoken.html',
                controller: UserTokenController,
                controllerAs: 'vm',
            },
        },
        ncyBreadcrumb: {
            label: 'account',
        },
    });
}

/**
 * PreferencesUserProfile is a controller to show the user profile page.
 */
angular.module('app.preferences').controller('UserTokenController', UserTokenController);

UserTokenController.$inject = ['User'];
function UserTokenController(User) {
    var vm = this;
    vm.token = '';

    vm.deleteToken = deleteToken;
    vm.generateToken = generateToken;

    activate();

    /////

    function activate() {
        // Get the token of the current user
        User.token(function(data) {
            if (data.auth_token) {
                vm.token = data.auth_token;
            } else {
                vm.token = '';
            }
        });
    }

    function deleteToken() {
        // Get the token of the current user
        User.deleteToken(function() {
            vm.token = '';
            toastr.success('And it\'s gone!', 'Token deleted');
        });
    }

    function generateToken() {
        // Get the token of the current user
        User.generateToken({}, function(data) {
            vm.token = data.auth_token;
            toastr.success('I\'ve created a new one', 'Token generated');
        });
    }
}
