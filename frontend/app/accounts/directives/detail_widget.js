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

AccountDetailWidgetController.$inject = ['Settings', 'Tenant'];
function AccountDetailWidgetController(Settings, Tenant) {
    var vm = this;

    vm.settings = Settings;

    vm.updateModel = updateModel;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });

    function updateModel(data, field) {
        return vm.updateCallback()(data, field);
    }
}
