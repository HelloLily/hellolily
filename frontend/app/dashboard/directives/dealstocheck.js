
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
            descending: true,
            column: 'next_step_date',  // string: current sorted column
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
            var filterQuery = 'stage:2 AND is_checked:false AND new_business:true AND archived:false';

            if (vm.table.selectedUserId) {
                filterQuery += ' AND assigned_to_id:' + vm.table.selectedUserId;
            }

            var dealPromise = Deal.getDeals('', 1, 20, vm.table.order.column, vm.table.order.descending, filterQuery);
            dealPromise.then(function(deals) {
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
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column', 'vm.table.selectedUserId'], function() {
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
