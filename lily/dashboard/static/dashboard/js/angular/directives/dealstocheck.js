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

    DealsToCheck.$inject = ['$scope', 'Cookie', 'Deal', 'User'];
    function DealsToCheck ($scope, Cookie, Deal, User) {
        Cookie.prefix ='dealsToCheckkWidget';

        var vm = this;
        vm.table = {
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'closing_date'  // string: current sorted column
            }),
            items: [],
            selectedUser: Cookie.getCookieValue('selectedUser')
        };

        vm.markDealAsChecked = markDealAsChecked;

        activate();

        ///////////

        function activate () {
            _watchTable();
            _getUsers();
        }

        function _getDealsToCheck () {
            if (vm.table.selectedUser) {
                Deal.getDealsToCheck(
                    vm.table.order.column,
                    vm.table.order.ascending,
                    vm.table.selectedUser.id
                ).then(function (deals) {
                    vm.table.items = deals;
                });
            }
        }

        function _getUsers() {
            vm.users = User.query();
        }

        function _watchTable() {
            $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column', 'vm.table.selectedUser'], function() {
                _getDealsToCheck();
            })
        }

        function markDealAsChecked (deal) {
            deal.markDealAsChecked().then(function() {
               vm.table.items.splice(vm.table.items.indexOf(deal), 1);
            });
        }

    }

})();
