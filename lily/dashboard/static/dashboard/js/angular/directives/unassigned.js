(function() {
    'use strict';

    /**
     * Controller for the UnassignedCases dashboard widget(s), which shows
     * a widget per team for unassigned cases.
     */
    angular.module('app.dashboard.directives').directive('unassignedCases', unassignedCases);

    function unassignedCases () {
        return {
            templateUrl: 'dashboard/unassignedcases.html',
            controller: UnassignedCases,
            controllerAs: 'uc',
            bindToController: true,
            scope: {
                team: '='
            }
        }
    }

    UnassignedCases.$inject = ['$http', '$scope', 'Case', 'Cookie'];
    function UnassignedCases ($http, $scope, Case, Cookie) {
        var vm = this;
        Cookie.prefix = 'unassignedCasesForTeam' + vm.team.id + 'Widget';

        vm.table = {
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'id'  // string: current sorted column
            }),
            items: []
        };

        vm.assignToMe = assignToMe;

        activate();

        /////

        function activate() {
            _watchTable();
        }

        function _getUnassignedCases() {
            Case.getUnassignedCasesForTeam(
                vm.team.id,
                vm.table.order.column,
                vm.table.order.ascending
            ).then(function(cases) {
                vm.table.items = cases;
            });
        }

        function assignToMe (caseObj){
            if(confirm('Assign this case to yourself?')){
                var req = {
                    method: 'POST',
                    url: '/cases/update/assigned_to/' + caseObj.id + '/',
                    data: 'assignee=' + currentUser.id,
                    headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
                };

                $http(req).success(function() {
                    vm.table.items.splice(vm.table.items.indexOf(caseObj), 1);
                    $scope.loadNotifications();
                });
            }
        }

        function _watchTable() {
            $scope.$watchGroup(['uc.table.order.ascending', 'uc.table.order.column'], function() {
                 _getUnassignedCases();
            })
        }
    }
})();
