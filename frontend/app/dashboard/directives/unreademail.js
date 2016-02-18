angular.module('app.dashboard.directives').directive('unreadEmail', unreadEmailDirective);

function unreadEmailDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/unreademail.html',
        controller: UnreadEmailController,
        controllerAs: 'vm',
    };
}

UnreadEmailController.$inject = ['$scope', 'EmailMessage', 'HLUtils', 'LocalStorage'];
function UnreadEmailController($scope, EmailMessage, HLUtils, LocalStorage) {
    var storage = LocalStorage('unreadEmailWidget');

    var vm = this;
    vm.table = {
        order: storage.get('order', {
            descending: true,
            column: 'sent_date',  // string: current sorted column
        }),
        items: [],
    };
    activate();

    //////

    function activate() {
        _watchTable();
    }

    function _getMessages() {
        HLUtils.blockUI('#unreadEmailBlockTarget', true);

        EmailMessage.getDashboardMessages(
            vm.table.order.column,
            vm.table.order.descending
        ).then(function(messages) {
            vm.table.items = messages;

            HLUtils.unblockUI('#unreadEmailBlockTarget');
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getMessages();
            storage.put('order', vm.table.order);
        });
    }
}
