(function() {
    'use strict';

    /**
     * CallbackRequests widget
     */
    angular.module('app.dashboard.directives').directive('callbackRequests', callbackRequests);

    function callbackRequests () {
        return {
            templateUrl: 'dashboard/callbackrequests.html',
            controller: CallbackRequests,
            controllerAs: 'cbr'
        }
    }

    CallbackRequests.$inject = ['$scope', 'Case', 'Cookie'];
    function CallbackRequests ($scope, Case, Cookie) {
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
            $scope.$watchGroup(['cbr.table.order.ascending', 'cbr.table.order.column'], function() {
                _getCallbackRequests();
                cookie.put('order', vm.table.order);
            })
        }

    }
})();
