angular.module('app.cases').controller('CaseAssignModal', CaseAssignModal);

CaseAssignModal.$inject = ['$modalInstance', 'myCase', 'Case', 'User'];
function CaseAssignModal ($modalInstance, myCase, Case, User) {
    var vm = this;
    vm.myCase = myCase;
    vm.currentAssigneeId = myCase.assigned_to_id;
    vm.users = [];

    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    ////

    function activate() {
        _getUsers();
    }

    function _getUsers() {
        User.query({}, function(data) {
            vm.users = data;
        });
    }

    function ok () {
        // Update the assigned_to of the case and close the modal
        Case.update({id: vm.myCase.id, assigned_to: vm.currentAssigneeId}).$promise.then(function () {
            $modalInstance.close();
        });
    }

    function cancel () {
        $modalInstance.dismiss('cancel');
    }
}
