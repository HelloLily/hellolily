(function() {
    'use strict';

    angular.module('DealControllers').controller('FollowUpWidgetModal', FollowUpWidgetModal);

    FollowUpWidgetModal.$inject = ['$filter', '$modalInstance', '$scope', '$interval', 'Deal', 'DealStages', 'followUp'];
    function FollowUpWidgetModal($filter, $modalInstance, $scope, $interval, Deal, DealStages, followUp){
        var vm = this;
        vm.dealStages = [];
        vm.selectedStage = { id: followUp.stage, name: followUp.stage_name };
        vm.followUp = followUp;
        vm.pickerIsOpen = false;
        vm.closingDate = new Date(followUp.closing_date);
        vm.dateFormat = 'dd MMMM yyyy';
        vm.datepickerOptions = {
            startingDay: 1
        };

        vm.openDatePicker = openDatePicker;
        vm.saveModal = saveModal;
        vm.closeModal = closeModal;

        activate();

        function activate(){
            _getDealStages();
        }

        function _getDealStages(){
            DealStages.query({}, function(data){
                vm.dealStages = [];
                for(var i = 0; i < data.length; i++){
                    vm.dealStages.push({ id: data[i][0], name: data[i][1]});
                }
            });
        }

        function saveModal(){
            var newDate = $filter('date')(vm.closingDate, 'yyyy-MM-dd');
            var newStage = vm.selectedStage.id;
            Deal.update({id: followUp.id}, {stage: newStage, expected_closing_date: newDate}, function() {
                $modalInstance.close();
            });
        }

        function openDatePicker($event){
            $event.preventDefault();
            $event.stopPropagation();
            vm.pickerIsOpen = true;
        }

        function closeModal(){
            $modalInstance.close();
        }
    }
})();