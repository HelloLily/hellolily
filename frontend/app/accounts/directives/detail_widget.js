angular.module('app.accounts.directives').directive('accountDetailWidget', accountDetailWidget);

function accountDetailWidget() {
    return {
        restrict: 'E',
        scope: {
            account: '=',
            height: '=',
        },
        templateUrl: 'accounts/directives/detail_widget.html',
        controller: AccountDetailWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

AccountDetailWidgetController.$inject = ['Settings', 'Tenant'];
function AccountDetailWidgetController(Settings, Tenant) {
    var vm = this;
    vm.settings = Settings;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });
}
