angular.module('app.dashboard.directives').directive('followUp', followUpDirective);

function followUpDirective() {
    return {
        scope: {},
        templateUrl: 'dashboard/directives/followup.html',
        controller: FollowUpController,
        controllerAs: 'vm',
    };
}

FollowUpController.$inject = ['$uibModal', '$scope', 'Deal', 'LocalStorage'];
function FollowUpController($uibModal, $scope, Deal, LocalStorage) {
    var storage = LocalStorage('followupWidget');
    var vm = this;

    vm.table = {
        order: storage.get('order', {
            descending: true,
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
        var filterQuery = '(stage: 0 OR stage: 1 OR stage: 4 OR stage: 5) AND assigned_to_id: ' + currentUser.id;
        var dealPromise = Deal.getDeals('', 1, 20, vm.table.order.column, vm.table.order.descending, filterQuery);

        dealPromise.then(function(data) {
            vm.table.items = data;
        });
    }

    function openFollowUpWidgetModal(followUp) {
        var modalInstance = $uibModal.open({
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
        $scope.$watchGroup(['vm.table.order.descending', 'vm.table.order.column'], function() {
            _getFollowUp();
            storage.put('order', vm.table.order);
        });
    }
}
