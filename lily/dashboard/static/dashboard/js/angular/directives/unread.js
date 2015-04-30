(function() {
    'use strict';

    /**
     * Unread Email Widget
     */
    angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmail);

    function unreadEmail () {
        return {
            templateUrl: 'dashboard/unreademail.html',
            controller: UnreadEmail,
            controllerAs: 'ue'
        }
    }

    UnreadEmail.$inject = ['$scope', 'EmailMessage', 'Cookie'];
    function UnreadEmail ($scope, EmailMessage, Cookie) {

        Cookie.prefix ='unreadEmailWidget';

        var vm = this;
        vm.table = {
            order: Cookie.getCookieValue('order', {
                ascending: true,
                column: 'sent_date'  // string: current sorted column
            }),
            items: []
        };
        activate();

        //////

        function activate() {
            _watchTable();
        }

        function _getMessages () {
            EmailMessage.getDashboardMessages(
                vm.table.order.column,
                vm.table.order.ascending
            ).then(function (messages) {
                vm.table.items = messages;
            });
        }

        function _watchTable() {
            $scope.$watchGroup(['ue.table.order.ascending', 'ue.table.order.column'], function() {
                _getMessages();
            })
        }
    }
})();
