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
    const vm = this;

    vm.settings = Settings;
    vm.assignAccount = assignAccount;
    vm.currentUser = currentUser;

    activate();

    ////

    function activate() {
        if (typeof vm.clickableHeader === 'undefined') {
            vm.clickableHeader = true;
        }
    }

    vm.updateModel = updateModel;

    Tenant.query({}, tenant => {
        vm.tenant = tenant;
    });

    function updateModel(data, field) {
        return Account.updateModel(data, field, vm.account);
    }

    function assignAccount() {
        vm.account.assigned_to = currentUser;
        vm.account.assigned_to.full_name = currentUser.fullName;

        // Broadcast function to update model correctly after dynamically
        // changing the assignee by using the 'assign to me' link.
        $scope.$broadcast('activateEditableSelect', currentUser.id);

        return updateModel(currentUser.id, 'assigned_to');
    }
}
