(function () {
    'use strict';

    /**
     * DealsToCheck widget
     */
    angular.module('app.dashboard.directives').directive('dealsToCheck', dealsToCheck);

    function dealsToCheck () {
        return {
            scope: {},
            templateUrl: 'dashboard/dealstocheck.html',
            controller: DealsToCheck,
            controllerAs: 'vm'
        }
    }

    DealsToCheck.$inject = ['$scope', 'Cookie', 'Deal', 'UserTeams'];
    function DealsToCheck ($scope, Cookie, Deal, UserTeams) {
        var cookie = Cookie('dealsToCheckkWidget');
        var vm = this;
        vm.users = [];
        vm.table = {
            order: cookie.get('order', {
                ascending: true,
                column: 'closing_date'  // string: current sorted column
            }),
            items: [],
            selectedUserId: cookie.get('selectedUserId')
        };
        vm.markDealAsChecked = markDealAsChecked;
        activate();

        ///////////

        function activate () {
            _watchTable();
            _getUsers();
        }

        function _getDealsToCheck () {
            if (vm.table.selectedUserId) {
                Deal.getDealsToCheck(
                    vm.table.order.column,
                    vm.table.order.ascending,
                    vm.table.selectedUserId
                ).then(function (deals) {
                    vm.table.items = deals;
                });
            }
        }

        function _getUsers() {
            UserTeams.mine(function (teams) {
                angular.forEach(teams, function (team) {
                    vm.users = vm.users.concat(team.user_set);
                });
            });
        }

        function _watchTable() {
            $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column', 'vm.table.selectedUserId'], function() {
                _getDealsToCheck();
                cookie.put('order', vm.table.order);
                cookie.put('selectedUserId', vm.table.selectedUserId);
            })
        }

        function markDealAsChecked (deal) {
            deal.markDealAsChecked().then(function() {
               vm.table.items.splice(vm.table.items.indexOf(deal), 1);
            });
        }

    }

})();
