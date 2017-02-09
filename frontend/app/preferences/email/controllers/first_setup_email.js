angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig($stateProvider) {
    $stateProvider.state('base.preferences.emailaccounts.setup', {
        url: '/setup',
        views: {
            '@': {
                templateUrl: 'preferences/email/controllers/first_setup_email.html',
                controller: EmailAccountSetupController,
                controllerAs: 'vm',
            },
        },
        resolve: {
            user: ['User', function(User) {
                return User.me().$promise;
            }],
        },
    });
}

angular.module('app.preferences').controller('EmailAccountSetupController', EmailAccountSetupController);

EmailAccountSetupController.$inject = ['$state', 'User', 'user'];
function EmailAccountSetupController($state, User, user) {
    var vm = this;

    vm.skipEmailAccountSetup = skipEmailAccountSetup;

    ////

    function skipEmailAccountSetup() {
        User.skipEmailAccountSetup().$promise.then(function(response) {
            currentUser.emailAccountStatus = response.info.email_account_status;
            $state.go('base.dashboard', {}, {reload: true});
        });
    }
}
