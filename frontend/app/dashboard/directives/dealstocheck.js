
angular.module('app.dashboard.directives').directive('dealsToCheck', dealsToCheckDirective);

function dealsToCheckDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/dealstocheck.html',
        controller: DealsToCheckController,
        controllerAs: 'vm',
    };
}

DealsToCheckController.$inject = ['$scope', 'LocalStorage', 'Deal', 'UserTeams'];
function DealsToCheckController($scope, LocalStorage, Deal, UserTeams) {
    var storage = LocalStorage('dealsToCheckkWidget');
    var vm = this;
    vm.users = [];
    vm.table = {
        order: storage.get('order', {
            ascending: true,
            column: 'closing_date',  // string: current sorted column
        }),
        items: [],
        selectedUserId: storage.get('selectedUserId'),
    };
    vm.markDealAsChecked = markDealAsChecked;
    activate();

    ///////////

    function activate() {
        _watchTable();
        _getUsers();
    }

    function _getDealsToCheck() {
        if (vm.table.selectedUserId) {
            Deal.getDealsToCheck(
                vm.table.order.column,
                vm.table.order.ascending,
                vm.table.selectedUserId
            ).then(function(deals) {
                vm.table.items = deals;
            });
        }
    }

    function _getUsers() {
        UserTeams.mine(function(teams) {
            angular.forEach(teams, function(team) {
                vm.users = vm.users.concat(team.user_set);
            });
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column', 'vm.table.selectedUserId'], function() {
            _getDealsToCheck();
            storage.put('order', vm.table.order);
            storage.put('selectedUserId', vm.table.selectedUserId);
        });
    }

    function markDealAsChecked(deal) {
        deal.markDealAsChecked().then(function() {
            vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }

}
