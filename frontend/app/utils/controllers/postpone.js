angular.module('app.cases').controller('PostponeModal', PostponeModal);

PostponeModal.$inject = ['$uibModalInstance', '$scope', 'data', '$injector', 'HLUtils'];
function PostponeModal($uibModalInstance, $scope, data, $injector, HLUtils) {
    var vm = this;

    vm.type = data.type;
    vm.object = data.object;
    vm.dateField = data.dateField;
    vm.pickerIsOpen = false;
    vm.dateFormat = 'dd MMMM yyyy';
    vm.datepickerOptions = {
        startingDay: 1,
    };

    vm.disabledDates = disabledDates;
    vm.openDatePicker = openDatePicker;
    vm.postponeWithDays = postponeWithDays;
    vm.getFutureDate = getFutureDate;

    activate();

    ////

    function activate() {
        if (vm.object[vm.dateField]) {
            vm.date = moment(vm.object[vm.dateField]);
        } else {
            vm.date = moment();
        }

        vm.date = vm.date.format();

        _watchCloseDatePicker();
    }

    /**
     * When the datepicker popup is closed, update model and close modal.
     *
     * @private
     */
    function _watchCloseDatePicker() {
        $scope.$watch('vm.pickerIsOpen', function(newValue, oldValue) {
            if (!newValue && oldValue) {
                _updateDayAndCloseModal();
            }
        });
    }

    function _updateDayAndCloseModal() {
        var newDate;
        var args;

        if (!moment(vm.date).isSame(moment(vm.object[vm.dateField]))) {
            // Update the due date for this case.
            newDate = moment(vm.date).format('YYYY-MM-DD');

            args = {
                id: vm.object.id,
            };

            args[vm.dateField] = newDate;
            // Update the model so changes are reflected instantly.
            vm.object[vm.dateField] = newDate;

            // Dynamically get the model that should be updated.
            $injector.get(vm.type).patch(args, function() {
                $uibModalInstance.close();
            });
        } else {
            $uibModalInstance.close();
        }
    }

    function disabledDates(currentDate, mode) {
        var date = moment.isMoment(currentDate) ? currentDate : moment(currentDate);

        // Disable Saturday and Sunday.
        return ( mode === 'day' && ( date.day() === 6 || date.day() === 0 ) );
    }

    function openDatePicker($event) {
        $event.preventDefault();
        $event.stopPropagation();
        vm.pickerIsOpen = true;
    }

    function postponeWithDays(days) {
        vm.date = getFutureDate(days);

        _updateDayAndCloseModal();
    }

    function getFutureDate(days) {
        var futureDate = moment();

        if (futureDate.isBefore(vm.date)) {
            futureDate = moment(vm.date);
        }

        futureDate = HLUtils.addBusinessDays(days, futureDate);

        return futureDate;
    }
}
