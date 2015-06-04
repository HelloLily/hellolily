angular.module('app.cases').controller('CasePostponeModal', CasePostponeModal);

CasePostponeModal.$inject = ['$filter', '$modalInstance', '$scope', 'Case', 'myCase'];
function CasePostponeModal ($filter, $modalInstance, $scope, Case, myCase) {
    var vm = this;
    vm.myCase = myCase;
    vm.pickerIsOpen = false;
    vm.expireDate = new Date(myCase.expires);
    vm.dateFormat = 'dd MMMM yyyy';
    vm.datepickerOptions = {
        startingDay: 1
    };

    vm.disabledDates = disabledDates;
    vm.openDatePicker = openDatePicker;
    vm.postponeWithDays = postponeWithDays;
    vm.getFutureDate = getFutureDate;

    activate();

    ////

    function activate() {
        _watchCloseDatePicker();
    }

    /**
     * When the datepicker popup is closed, update model and close modal
     *
     * @private
     */
    function _watchCloseDatePicker () {
        $scope.$watch('vm.pickerIsOpen', function(newValue, oldValue) {
            if (!newValue && oldValue) {
                _updateDayAndCloseModal();
            }
        });
    }

    function _updateDayAndCloseModal() {
        if (vm.expireDate != new Date(myCase.expires)) {
            // Update the expire date for this case
            var newDate = $filter('date')(vm.expireDate, 'yyyy-MM-dd');
            Case.update({id: myCase.id}, {expires: newDate}, function() {
                $modalInstance.close();
            })
        } else {
            $modalInstance.close();
        }
    }
    function disabledDates (date, mode) {
        return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
    }

    function openDatePicker ($event) {
        $event.preventDefault();
        $event.stopPropagation();
        vm.pickerIsOpen = true;
    }

    function postponeWithDays (days) {
        vm.expireDate.setDate(vm.expireDate.getDate() + days);
        _updateDayAndCloseModal();
    }

    function getFutureDate(days) {
        var futureDate = new Date(vm.expireDate);
        return futureDate.setDate(futureDate.getDate() + days);
    }
}
