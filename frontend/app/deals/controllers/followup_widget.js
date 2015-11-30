angular.module('app.deals').controller('FollowUpWidgetModal', FollowUpWidgetModalController);

FollowUpWidgetModalController.$inject = ['$modalInstance', 'Deal', 'DealStages', 'followUp'];
function FollowUpWidgetModalController($modalInstance, Deal, DealStages, followUp) {
    var vm = this;
    vm.dealStages = [];
    vm.selectedStage = {id: followUp.stage, name: followUp.stage_name};
    vm.followUp = followUp;
    vm.pickerIsOpen = false;
    vm.dateFormat = 'dd MMMM yyyy';
    vm.datepickerOptions = {
        startingDay: 1,
    };

    vm.openDatePicker = openDatePicker;
    vm.saveModal = saveModal;
    vm.closeModal = closeModal;

    activate();

    function activate() {
        _getDealStages();
    }

    function _getDealStages() {
        DealStages.query({}, function(data) {
            vm.dealStages = [];
            for (var i = 0; i < data.length; i++) {
                vm.dealStages.push({id: data[i][0], name: data[i][1]});
            }
        });
    }

    function saveModal() {
        var newStage = vm.selectedStage.id;
        Deal.update({id: followUp.id}, {stage: newStage}, function() {
            $modalInstance.close();
        });
    }

    function openDatePicker($event) {
        $event.preventDefault();
        $event.stopPropagation();
        vm.pickerIsOpen = true;
    }

    function closeModal() {
        $modalInstance.close();
    }
}
