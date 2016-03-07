angular.module('app.deals').controller('WhyLostModal', WhyLostModal);

WhyLostModal.$inject = ['$uibModalInstance', 'Deal'];
function WhyLostModal($uibModalInstance, Deal) {
    var vm = this;

    vm.ok = ok;
    vm.cancel = cancel;

    activate();

    ////

    function activate() {
        _getWhyLost();
    }

    function _getWhyLost() {
        Deal.getWhyLost(function(response) {
            vm.whyLostChoices = response.results;
        });
    }

    function ok() {
        $uibModalInstance.close(vm.whyLost);
    }

    function cancel() {
        $uibModalInstance.dismiss('cancel');
    }
}
