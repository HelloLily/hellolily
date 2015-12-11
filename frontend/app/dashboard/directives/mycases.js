angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm',
    };
}

MyCasesController.$inject = ['$scope', 'Case', 'HLUtils', 'LocalStorage'];
function MyCasesController($scope, Case, HLUtils, LocalStorage) {
    var storage = LocalStorage('myCasesWidget');
    var vm = this;

    vm.highPrioCases = 0;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'priority', // string: current sorted column
        }),
        items: [],
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
    };

    vm.numOfCases = 0;

    vm.getMyCases = getMyCases;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function getMyCases() {
        var field = 'expires';
        var descending = false;

        if (vm.table.dueDateFilter !== '') {
            field = vm.table.order.column;
            descending = vm.table.order.descending;
        }

        Case.getMyCasesWidget(
            field,
            descending,
            vm.table.dueDateFilter,
            vm.table.usersFilter
        ).then(function(data) {
            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': data,
                };
            } else {
                vm.table.items = HLUtils.timeCategorizeObjects(data, 'expires');
            }

            vm.highPrioCases = 0;

            for (var i in data) {
                if (data[i].priority === 3) {
                    vm.highPrioCases++;
                }
            }

            vm.numOfCases = data.length;
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            getMyCases();
            storage.put('order', vm.table.order);
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }
}
