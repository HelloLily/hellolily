angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm',
    };
}

MyCasesController.$inject = ['$scope', 'Case', 'Cookie'];
function MyCasesController($scope, Case, Cookie) {
    var cookie = Cookie('myCasesWidget');

    var vm = this;
    vm.highPrioCases = 0;
    vm.table = {
        order: {
            ascending: true,
            column: 'priority', // string: current sorted column
        },
        items: [],
        expiresFilter: cookie.get('expiresFilter', ''),
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
                // ng-repeat sorts keys alphabetically, so for now setup the cases this way.
                // Angular 1.4 should no longer sort alphabetically, so this could be changed later on.
                var cases = [
                    {name: 'Expired', cases: []},
                    {name: 'Today', cases: []},
                    {name: 'Tomorrow', cases: []},
                    {name: 'Later', cases: []},
                ];

                var now = moment();
                var tomorrow = moment().add('1', 'day');

                angular.forEach(data, function(myCase) {
                    var day = moment(myCase.expires);

                    if (day.isBefore(now, 'day')) {
                        cases[0].cases.push(myCase);
                    } else if (day.isSame(now, 'day')) {
                        cases[1].cases.push(myCase);
                    } else if (day.isSame(tomorrow, 'day')) {
                        cases[2].cases.push(myCase);
                    } else {
                        cases[3].cases.push(myCase);
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
            cookie.put('expiresFilter', vm.table.expiresFilter);
        });
    }
}
