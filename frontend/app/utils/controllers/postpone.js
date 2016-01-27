angular.module('app.cases').controller('PostponeModal', PostponeModal);

PostponeModal.$inject = ['$filter', '$uibModalInstance', '$scope', 'data', '$injector'];
function PostponeModal($filter, $uibModalInstance, $scope, data, $injector) {
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
     * When the datepicker popup is closed, update model and close modal
     *
     * @private
     */
    function _watchCloseDatePicker() {
        $scope.$watch('vm.pickerIsOpen', function(newValue, oldValue) {
            if (!newValue && oldValue) {
                vm.date = vm.pickerDate;
                _updateDayAndCloseModal();
            }
        });
    }

    function _updateDayAndCloseModal() {
        if (!moment(vm.date).isSame(moment(vm.object[vm.dateField]))) {
            // Update the due date for this case.
            var newDate = moment(vm.date).format('YYYY-MM-DD');

            var args = {
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

    function disabledDates(date, mode) {
        if (!moment.isMoment(date)) {
            date = moment(date);
        }

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

        // Only skip weekends if we're postponing by 1 or 2 days.
        if (days !== 7 && futureDate.day() >= 5) {
            // Day is Saturday, so get the next monday and add the amount of days.
            futureDate = futureDate.add(1, 'week').day(days);
        } else if (days !== 7 && futureDate.day() === 0) {
            // Day is Sunday, which is a new week, so get the Monday and add the amount of days.
            futureDate = futureDate.day(1).day(days);
        } else {
            futureDate = futureDate.add(days, 'days');
        }

        return futureDate.format('YYYY-MM-DD');
    }
}
