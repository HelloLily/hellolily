angular.module('app.accounts.directives').directive('accountDetailWidget', accountDetailWidget);

function accountDetailWidget() {
    return {
        restrict: 'E',
        scope: {
            account: '=',
            height: '=',
            updateCallback: '&',
            clickableHeader: '=?',
        },
        templateUrl: 'accounts/directives/detail_widget.html',
        controller: AccountDetailWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

AccountDetailWidgetController.$inject = ['$scope', 'Account', 'Settings', 'Tenant'];
function AccountDetailWidgetController($scope, Account, Settings, Tenant) {
    var vm = this;

    vm.settings = Settings;

    activate();

    ////

    function activate() {
        if (typeof vm.clickableHeader === 'undefined') {
            vm.clickableHeader = true;
        }
    }

    vm.updateModel = updateModel;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });

    function updateModel(data, field) {
        return Account.updateModel(data, field, vm.account);
    }
}
