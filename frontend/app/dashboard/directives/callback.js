angular.module('app.dashboard.directives').directive('callbackRequests', CallbackRequestsDirective);

function CallbackRequestsDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/callback.html',
        controller: CallbackRequestsController,
        controllerAs: 'vm'
    }
}

CallbackRequestsController.$inject = ['$scope', 'Case', 'Cookie'];
function CallbackRequestsController ($scope, Case, Cookie) {
    var vm = this;
    var cookie = Cookie('callbackWidget');

    vm.table = {
        order: cookie.get('order', {
            ascending: true,
            column: 'created'  // string: current sorted column
        }),
        items: []
    };

    activate();

    ///////////

    function activate () {
        _watchTable();
    }

    function _getCallbackRequests () {
        Case.getCallbackRequests(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function (callbackRequests) {
            vm.table.items = callbackRequests;
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getCallbackRequests();
            cookie.put('order', vm.table.order);
        })
    }
}
