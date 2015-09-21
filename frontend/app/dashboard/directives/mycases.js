angular.module('app.dashboard.directives').directive('myCases', myCasesDirective);

function myCasesDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/mycases.html',
        controller: MyCasesController,
        controllerAs: 'vm'
    }
}

MyCasesController.$inject = ['$modal', '$scope', 'Case', 'Cookie'];
function MyCasesController ($modal, $scope, Case, Cookie) {
    var cookie = Cookie('myCasesWidget');

    var vm = this;
    vm.highPrioCases = 0;
    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'expires'  // string: current sorted column
        }),
        items: [],
        expiresFilter: cookie.get('expiresFilter', '')
    };

    vm.openPostponeWidget = openPostponeWidget;

    activate();

    /////

    function activate() {
        _watchTable();
    }

    function _getMyCases() {
        Case.getMyCasesWidget(
            vm.table.order.column,
            vm.table.order.ascending,
            vm.table.expiresFilter
        ).then(function (data) {
            vm.table.items = data;
            vm.highPrioCases = 0;
            for (var i in data) {
                if (data[i].priority == 3) {
                    vm.highPrioCases++;
                }
            }
        });
    }

    function openPostponeWidget(myCase) {
        var modalInstance = $modal.open({
            templateUrl: 'cases/controllers/postpone.html',
            controller: 'CasePostponeModal',
            controllerAs: 'vm',
            size: 'sm',
            resolve: {
                myCase: function() {
                    return myCase
                }
            }
        });

        modalInstance.result.then(function() {
            _getMyCases();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column', 'vm.table.expiresFilter'], function() {
            _getMyCases();
            cookie.put('order', vm.table.order);
            cookie.put('expiresFilter', vm.table.expiresFilter);
        });
    }
}
