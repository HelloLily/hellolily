angular.module('app.cases').controller('CaseAssignModal', CaseAssignModal);

CaseAssignModal.$inject = ['$modalInstance', 'myCase', 'Case', 'User'];
function CaseAssignModal($modalInstance, myCase, Case, User) {
    var vm = this;
    vm.myCase = myCase;
    vm.users = [];

    vm.ok = ok;
    vm.cancel = cancel;
    vm.assignToMe = assignToMe;

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

    function assignToMe() {
        vm.assignee = {
            id: currentUser.id,
            full_name: currentUser.fullName,
        };
    }

    function ok() {
        // Update the assigned_to of the case and close the modal
        Case.update({id: vm.myCase.id, assigned_to: vm.assignee.id}).$promise.then(function() {
            $modalInstance.close();
        });
    }

    function cancel() {
        $modalInstance.dismiss('cancel');
    }
}
