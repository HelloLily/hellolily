angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm',
    };
}

MyCasesController.$inject = ['$scope', 'Case', 'LocalStorage'];
function MyCasesController($scope, Case, LocalStorage) {
    var storage = LocalStorage('myCasesWidget');

    var vm = this;
    vm.highPrioCases = 0;
    vm.table = {
        order: storage.get('order', {
            ascending: true,
            column: 'priority', // string: current sorted column
        }),
        items: [],
        dueDateFilter: storage.get('dueDateFilter', ''),
        usersFilter: storage.get('usersFilter', ''),
    };

    vm.openPostponeWidget = openPostponeWidget;
    vm.numOfCases = 0;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getMyCases() {
        var field = '';
        var sorting = false;

        if (vm.dueDateFilter !== '') {
            field = vm.table.order.column;
            sorting = vm.table.order.ascending;
        } else {
            field = 'expires';
            sorting = false;
        }

        Case.getMyCasesWidget(
            field,
            sorting,
            vm.table.dueDateFilter,
            vm.table.usersFilter
        ).then(function(data) {
            if (vm.table.dueDateFilter !== '') {
                // Add empty key to prevent showing a header and to not crash the for loop.
                vm.table.items = {
                    '': data,
                };
            } else {
                var now = moment();
                var tomorrow = moment().add('1', 'day');

                var cases = {
                    expired: [],
                    today: [],
                    tomorrow: [],
                    later: [],
                };

                angular.forEach(data, function(myCase) {
                    var day = moment(myCase.expires);

                    if (day.isBefore(now, 'day')) {
                        cases.expired.push(myCase);
                    } else if (day.isSame(now, 'day')) {
                        cases.today.push(myCase);
                    } else if (day.isSame(tomorrow, 'day')) {
                        cases.tomorrow.push(myCase);
                    } else {
                        cases.later.push(myCase);
                    }
                });

                vm.table.items = cases;
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

    function openPostponeWidget(myCase) {
        var modalInstance = Case.openPostponeWidget(myCase, true);

        modalInstance.result.then(function() {
            _getMyCases();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.dueDateFilter', 'vm.table.usersFilter'], function() {
            _getMyCases();
            storage.put('order', vm.table.order);
            storage.put('dueDateFilter', vm.table.dueDateFilter);
            storage.put('usersFilter', vm.table.usersFilter);
        });
    }
}
