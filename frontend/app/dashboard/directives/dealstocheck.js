
angular.module('app.dashboard.directives').directive('dealsToCheck', dealsToCheckDirective);

function dealsToCheckDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/dealstocheck.html',
        controller: DealsToCheckController,
        controllerAs: 'vm',
    };
}

DealsToCheckController.$inject = ['$scope', 'LocalStorage', 'Deal', 'HLUtils', 'UserTeams'];
function DealsToCheckController($scope, LocalStorage, Deal, HLUtils, UserTeams) {
    var storage = LocalStorage('dealsToCheckkWidget');
    var vm = this;

    vm.users = [];
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        items: [],
        usersFilter: storage.get('usersFilter', ''),

    };
    vm.markDealAsChecked = markDealAsChecked;
    activate();

    ///////////

    function activate() {
        _watchTable();
        _getUsers();
    }

    function _getDealsToCheck() {
        var filterQuery = 'stage:2 AND is_checked:false AND new_business:true AND archived:false';
        var dealPromise;

        HLUtils.blockUI('#dealsToCheckBlockTarget', true);

        if (vm.table.usersFilter) {
            filterQuery += ' AND (' + vm.table.usersFilter + ')';
        } else {
            filterQuery += ' AND assigned_to_id:' + currentUser.id;
        }

        dealPromise = Deal.getDeals('', 1, 20, vm.table.order.column, vm.table.order.descending, filterQuery);
        dealPromise.then(function(deals) {
            vm.table.items = deals;

            HLUtils.unblockUI('#dealsToCheckBlockTarget');
        });
    }

    function _getUsers() {
        UserTeams.mine(function(teams) {
            angular.forEach(teams, function(team) {
                vm.users = vm.users.concat(team.user_set);
            });
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column', 'vm.table.usersFilter'], function() {
            _getDealsToCheck();
            storage.put('order', vm.table.order);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }

    function markDealAsChecked(deal) {
        deal.markDealAsChecked().then(function() {
            vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }
}
