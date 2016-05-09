angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm',
    };
}

MyCasesController.$inject = ['$filter', '$scope', 'Case', 'HLUtils', 'LocalStorage'];
function MyCasesController($filter, $scope, Case, HLUtils, LocalStorage) {
    var storage = new LocalStorage('myCasesWidget');
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

        var filterQuery = 'archived:false AND NOT casetype_name:Callback';

        if (vm.table.dueDateFilter) {
            filterQuery += ' AND ' + vm.table.dueDateFilter;
        }

        if (vm.table.usersFilter) {
            filterQuery += ' AND (' + vm.table.usersFilter + ')';
        } else {
            filterQuery += ' AND assigned_to_id:' + currentUser.id;
        }

        HLUtils.blockUI('#myCasesBlockTarget', true);

        if (vm.table.dueDateFilter !== '') {
            field = vm.table.order.column;
            descending = vm.table.order.descending;
        }

        Case.getCases(field, descending, filterQuery).then(function(data) {
            var i;
            var objects = data.objects;
            // Make sure the data is sorted by priority as well.
            objects = $filter('orderBy')(objects, '-priority');

            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': objects,
                };
            } else {
                vm.table.items = HLUtils.timeCategorizeObjects(objects, 'expires');
            }

            vm.highPrioCases = 0;

            for (i in objects) {
                if (objects[i].priority === 3) {
                    vm.highPrioCases++;
                }
            }

            HLUtils.unblockUI('#myCasesBlockTarget');

            vm.numOfCases = objects.length;
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
