
angular.module('app.dashboard.directives').directive('dealsToCheck', dealsToCheckDirective);

function dealsToCheckDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/dealstocheck.html',
        controller: DealsToCheckController,
        controllerAs: 'vm',
    };
}

DealsToCheckController.$inject = ['$scope', 'Deal', 'HLResource', 'HLUtils', 'HLSockets', 'LocalStorage', 'UserTeams'];
function DealsToCheckController($scope, Deal, HLResource, HLUtils, HLSockets, LocalStorage, UserTeams) {
    var storage = new LocalStorage('dealsToCheckWidget');
    var vm = this;

    vm.users = [];
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'next_step_date',  // string: current sorted column
        }),
        items: [],
        usersFilter: storage.get('usersFilter', ''),
        conditions: {
            dueDate: false,
            user: false,
        },
    };
    vm.markDealAsChecked = markDealAsChecked;

    HLSockets.bind('deal-assigned', _getDealsToCheck);

    $scope.$on('$destroy', () => {
        HLSockets.unbind('deal-assigned', _getDealsToCheck);
    });

    activate();

    ///////////

    function activate() {
        _watchTable();
        _getUsers();
    }

    function _getDealsToCheck(blockUI = false) {
        Deal.getStatuses(function() {
            var filterQuery = 'status.id:' + Deal.wonStatus.id + ' AND is_checked:false AND new_business:true AND is_archived:false';

            if (blockUI) HLUtils.blockUI('#dealsToCheckBlockTarget', true);

            if (vm.table.usersFilter) {
                filterQuery += ' AND (' + vm.table.usersFilter + ')';
            }

            Deal.getDeals(vm.table.order.column, vm.table.order.descending, filterQuery).then(function(data) {
                vm.table.items = data.objects;

                if (blockUI) HLUtils.unblockUI('#dealsToCheckBlockTarget');
            });
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
            _getDealsToCheck(true);
            storage.put('order', vm.table.order);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }

    function markDealAsChecked(deal) {
        var args = {
            id: deal.id,
            is_checked: true,
        };

        HLResource.patch('Deal', args).$promise.then(function() {
            vm.table.items.splice(vm.table.items.indexOf(deal), 1);
        });
    }
}
