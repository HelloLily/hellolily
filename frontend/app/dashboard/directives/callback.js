angular.module('app.dashboard.directives').directive('callbackRequests', CallbackRequestsDirective);

function CallbackRequestsDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/callback.html',
        controller: CallbackRequestsController,
        controllerAs: 'vm',
    };
}

CallbackRequestsController.$inject = ['$scope', 'Case', 'HLUtils', 'LocalStorage'];
function CallbackRequestsController($scope, Case, HLUtils, LocalStorage) {
    var vm = this;
    var storage = LocalStorage('callbackWidget');

    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'created',  // string: current sorted column
        }),
        items: [],
    };

    activate();

    ///////////

    function activate () {
        _watchTable();
    }

    function _getCallbackRequests() {
        HLUtils.blockUI('#callbackBlockTarget', true);
        Case.getCallbackRequests(
            vm.table.order.column,
            vm.table.order.descending
        ).then(function(data) {
            vm.table.items = data.objects;

            HLUtils.unblockUI('#callbackBlockTarget');
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getCallbackRequests();
            storage.put('order', vm.table.order);
        });
    }
}
