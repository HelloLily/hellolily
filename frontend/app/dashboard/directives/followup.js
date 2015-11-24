angular.module('app.dashboard.directives').directive('followUp', followUpDirective);

function followUpDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/followup.html',
        controller: FollowUpController,
        controllerAs: 'vm',
    };
}

FollowUpController.$inject = ['$modal', '$scope', 'Deal', 'LocalStorage'];
function FollowUpController($modal, $scope, Deal, LocalStorage) {
    var storage = LocalStorage('followupWidget');
    var vm = this;

    vm.table = {
        order: storage.get('order', {
            ascending: true,
            column: 'created',
        }),
        items: [],
    };

    vm.openFollowUpWidgetModal = openFollowUpWidgetModal;

    activate();

    //////

    function activate() {
        _watchTable();
    }

    function _getFollowUp() {
        Deal.getFollowUpWidgetData(
            vm.table.order.column,
            vm.table.order.ascending
        ).then(function(data) {
            vm.table.items = data;
        });
    }

    function openFollowUpWidgetModal(followUp) {
        var modalInstance = $modal.open({
            templateUrl: 'deals/controllers/followup_widget.html',
            controller: 'FollowUpWidgetModal',
            controllerAs: 'vm',
            size: 'md',
            resolve: {
                followUp: function() {
                    return followUp;
                },
            },
        });

        modalInstance.result.then(function() {
            _getFollowUp();
        });
    }

    function _watchTable() {
        $scope.$watchGroup(['vm.table.order.ascending', 'vm.table.order.column'], function() {
            _getFollowUp();
            storage.put('order', vm.table.order);
        });
    }
}
