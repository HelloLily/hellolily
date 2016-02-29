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

UnassignedCasesController.$inject = ['$http', '$scope', '$state', 'Case', 'HLFilters', 'HLUtils', 'LocalStorage'];
function UnassignedCasesController($http, $scope, $state, Case, HLFilters, HLUtils, LocalStorage) {
    var vm = this;

    vm.storageName = 'unassignedCasesForTeam' + vm.team.id + 'Widget';
    vm.storage = new LocalStorage(vm.storageName);
    vm.storedFilterList = vm.storage.get('filterListSelected', null);
    vm.highPrioCases = 0;
    vm.table = {
        order: vm.storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };

    vm.assignToMe = assignToMe;
    vm.updateTable = updateTable;

    activate();

    /////

    function activate() {
        _watchTable();

        Case.caseTypes(function(caseTypes) {
            var filterList = [];

            angular.forEach(caseTypes, function(caseType) {
                filterList.push({
                    name: caseType.type,
                    value: 'casetype_id:' + caseType.id,
                    selected: false,
                    isSpecialFilter: true,
                });
            });

            HLFilters.getStoredSelections(filterList, vm.storedFilterList);

            vm.filterList = filterList;
        });
    }

    function updateTable() {
        var i;
        var filterQuery = 'archived:false AND _missing_:assigned_to_id AND assigned_to_groups:' + vm.team.id;

        HLUtils.blockUI('#unassignedCasesBlockTarget' + vm.team.id, true);

        if (vm.table.filterQuery) {
            filterQuery += ' AND ' + vm.table.filterQuery;
        }

        Case.getCases('', 1, 20, vm.table.order.column, vm.table.order.descending, filterQuery).then(function(data) {
            vm.table.items = data.objects;
            vm.highPrioCases = 0;

            for (i in data.objects) {
                if (data.objects[i].priority === 3) {
                    vm.highPrioCases++;
                }
            }

            HLUtils.unblockUI('#unassignedCasesBlockTarget' + vm.team.id);
        });
    }

    function assignToMe(caseObj) {
        var req;

        if (confirm('Assign this case to yourself?')) {
            req = {
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
            updateTable();
            vm.storage.put('order', vm.table.order);
        });
    }
}
