/**
 * Router definition.
 */
angular.module('app.accounts').config(accountConfig);

accountConfig.$inject = ['$stateProvider'];
function accountConfig ($stateProvider) {

    $stateProvider.state('base.accounts.detail.delete', {
        url: '/delete',
        views: {
            '@': {
                controller: 'AccountDeleteController'
            }
        }
    });
}

/**
 * Controller to delete a account
 */
angular.module('app.accounts').controller('AccountDeleteController', AccountDeleteController);

AccountDeleteController.$inject = ['$state', '$stateParams', 'Account'];
function AccountDeleteController ($state, $stateParams, Account) {
    var id = $stateParams.id;

    Account.delete({
        id:id
    }, function() {  // On success
        $state.go('base.accounts');
    }, function(error) {  // On error
        // Error notification needed
        $state.go('base.accounts');
    });
}
