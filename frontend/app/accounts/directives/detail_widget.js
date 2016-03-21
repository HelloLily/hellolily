/**
 * Account detail widget
 */
angular.module('app.accounts.directives').directive('accountDetailWidget', AccountDetailWidget);

function AccountDetailWidget() {
    return {
        restrict: 'E',
        replace: true,
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

AccountDetailWidgetController.$inject = ['Tenant'];
function AccountDetailWidgetController(Tenant) {
    var vm = this;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });
}
