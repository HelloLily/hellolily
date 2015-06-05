angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmailDirective);

function unreadEmailDirective () {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/unreademail.html',
        controller: UnreadEmailController,
        controllerAs: 'vm'
    }
}

UnreadEmailController.$inject = ['$scope', 'EmailMessage', 'Cookie'];
function UnreadEmailController ($scope, EmailMessage, Cookie) {
    var cookie = Cookie('unreadEmailWidget');

    var vm = this;
    vm.table = {
        order: cookie.get('order', {
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
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getMessages();
            cookie.put('order', vm.table.order);
        })
    }
}
