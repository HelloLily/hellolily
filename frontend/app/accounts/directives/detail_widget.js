angular.module('app.accounts.directives').directive('accountDetailWidget', accountDetailWidget);

function accountDetailWidget() {
    return {
        restrict: 'E',
        scope: {
            account: '=',
            height: '=',
            updateCallback: '&',
        },
        templateUrl: 'accounts/directives/detail_widget.html',
        controller: AccountDetailWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

AccountDetailWidgetController.$inject = ['Account', 'Settings', 'Tenant'];
function AccountDetailWidgetController(Account, Settings, Tenant) {
    var vm = this;

    vm.settings = Settings;

    vm.updateModel = updateModel;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });

    function updateModel(data, field) {
        return Account.updateModel(data, field, vm.account);
    }
}
