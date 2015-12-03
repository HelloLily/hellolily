angular.module('app.dashboard.directives').directive('unassignedCases', unassignedCasesDirective);

function unassignedCasesDirective() {
    return {
        templateUrl: 'dashboard/directives/unassignedcases.html',
        controller: UnassignedCasesController,
        controllerAs: 'vm',
        bindToController: true,
        scope: {
            team: '=',
        },
    };
}

UnassignedCasesController.$inject = ['$http', '$scope', '$state', 'Case', 'LocalStorage'];
function UnassignedCasesController($http, $scope, $state, Case, LocalStorage) {
    var vm = this;
    var storage = LocalStorage('unassignedCasesForTeam' + vm.team.id + 'Widget');
    vm.highPrioCases = 0;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };

    vm.assignToMe = assignToMe;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getUnassignedCases() {
        Case.getUnassignedCasesForTeam(
            vm.team.id,
            vm.table.order.column,
            vm.table.order.descending
        ).then(function(cases) {
            vm.table.items = cases;
            vm.highPrioCases = 0;
            for (var i in cases) {
                if (cases[i].priority == 3) {
                    vm.highPrioCases++;
                }
            }
        });
    }

    function assignToMe(caseObj) {
        if (confirm('Assign this case to yourself?')) {
            var req = {
                method: 'POST',
                url: '/cases/update/assigned_to/' + caseObj.id + '/',
                data: 'assignee=' + currentUser.id,
                headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'},
            };

            $http(req).success(function() {
                vm.table.items.splice(vm.table.items.indexOf(caseObj), 1);
                $state.go($state.current, {}, {reload: true});
            });
        }
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getUnassignedCases();
            storage.put('order', vm.table.order);
        });
    }
}
