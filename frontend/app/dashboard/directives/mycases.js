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
        },
        items: [],
        expiresFilter: storage.get('expiresFilter', ''),
    };

    vm.openPostponeWidget = openPostponeWidget;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getMyCases() {
        var field = '';
        var sorting = false;

        if (vm.expiresFilter !== '') {
            field = vm.table.order.column;
            sorting = vm.table.order.ascending;
        } else {
            field = 'expires';
            sorting = false;
        }

        Case.getMyCasesWidget(
            field,
            sorting,
            vm.table.expiresFilter
        ).then(function(data) {
            if (vm.table.expiresFilter !== '') {
                vm.table.items = data;
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
        });
    }

    function openPostponeWidget(myCase) {
        var modalInstance = Case.openPostponeWidget(myCase, true);

        modalInstance.result.then(function() {
            _getMyCases();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.expiresFilter'], function() {
            _getMyCases();
            storage.put('order', vm.table.order);
            storage.put('expiresFilter', vm.table.expiresFilter);
        });
    }
}
