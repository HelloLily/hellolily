angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm',
    };
}

MyCasesController.$inject = ['$filter', '$scope', 'Case', 'HLUtils', 'HLResource', 'HLSockets', 'LocalStorage'];
function MyCasesController($filter, $scope, Case, HLUtils, HLResource, HLSockets, LocalStorage) {
    const vm = this;
    const storage = new LocalStorage('myCasesWidget');

    vm.highPrioCases = 0;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'priority', // string: current sorted column
        }),
        items: [],
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
        conditions: {
            dueDate: false,
            user: false,
        },
    };
    vm.numOfCases = 0;

    vm.getMyCases = getMyCases;
    vm.acceptCase = acceptCase;
    vm.updateModel = updateModel;

    HLSockets.bind('case-assigned', getMyCases);

    $scope.$on('$destroy', () => {
        HLSockets.unbind('case-assigned', getMyCases);
    });

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function getMyCases(blockUI = false) {
        let field = 'expires';
        let descending = false;
        let filterQuery = 'is_archived:false';

        if (vm.table.dueDateFilter) {
            filterQuery += ' AND ' + vm.table.dueDateFilter;
        }

        if (vm.table.usersFilter) {
            filterQuery += ' AND (' + vm.table.usersFilter + ')';
        }

        if (blockUI) HLUtils.blockUI('#myCasesBlockTarget', true);

        if (vm.table.dueDateFilter !== '') {
            field = vm.table.order.column;
            descending = vm.table.order.descending;
        }

        Case.getCases(field, descending, filterQuery).then(data => {
            let objects = data.objects;
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

            for (let i in objects) {
                if (objects[i].priority === 3) {
                    vm.highPrioCases++;
                }
            }

            if (blockUI) HLUtils.unblockUI('#myCasesBlockTarget');

            vm.numOfCases = objects.length;
        });
    }

    function updateModel(data, field) {
        return Case.updateModel(data, field).then(() => {
            getMyCases(true);
        });
    }

    function acceptCase(myCase) {
        const args = {
            id: myCase.id,
            newly_assigned: false,
        };

        updateModel(args);
    }

    function _watchTable() {
        $scope.$watch('vm.table.dueDateFilter', (newValue, oldValue) => {
            if (newValue || oldValue) {
                getMyCases(true);
                storage.put('dueDateFilter', vm.table.dueDateFilter);
            }
        });

        $scope.$watch('vm.table.usersFilter', (newValue, oldValue) => {
            if (newValue || oldValue) {
                getMyCases(true);
                storage.put('usersFilter', vm.table.usersFilter);
            }
        });
    }
}
