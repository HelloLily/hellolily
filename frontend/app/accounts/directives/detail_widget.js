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

AccountDetailWidgetController.$inject = ['HLResource', 'Settings', 'Tenant'];
function AccountDetailWidgetController(HLResource, Settings, Tenant) {
    var vm = this;

    vm.settings = Settings;

    vm.updateModel = updateModel;

    Tenant.query({}, function(tenant) {
        vm.tenant = tenant;
    });

    function updateModel(data, field) {
        var args = HLResource.createArgs(data, field, vm.account);

        if (field === 'twitter') {
            args = {
                id: vm.account.id,
                social_media: [args],
            };
        }

        return HLResource.patch('Account', args).$promise;
    }
}
