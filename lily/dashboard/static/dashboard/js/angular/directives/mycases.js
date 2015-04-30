(function() {
    'use strict';

    /**
     * MyCases Widget
     */
    angular.module('app.dashboard.directives').directive('myCases', myCases);

    function myCases () {
        return {
            templateUrl: 'dashboard/mycases.html',
            controller: MyCases,
            controllerAs: 'mc'
        }
    }

    MyCases.$inject = ['$modal', '$scope', 'Case', 'Cookie'];
    function MyCases ($modal, $scope, Case, Cookie) {

        Cookie.prefix ='myCasesWidget';

        var vm = this;
        vm.table = {
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'expires'  // string: current sorted column
            }),
            items: []
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
                vm.table.order.ascending
            ).then(function (data) {
                vm.table.items = data;
            });
        }

        function openPostponeWidget(myCase) {
            var modalInstance = $modal.open({
                templateUrl: 'cases/casepostpone.modal.html',
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
            $scope.$watchGroup(['mc.table.order.ascending', 'mc.table.order.column'], function() {
                _getMyCases();
            })
        }
    }
})();
