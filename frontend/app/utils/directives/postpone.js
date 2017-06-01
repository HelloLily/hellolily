angular.module('app.utils.directives').directive('postpone', postponeDirective);

function postponeDirective() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
            type: '=',
            dateField: '=',
            callback: '&',
            ttPlacement: '@', // use tt instead of 'tooltip' for distinction.
            showIcon: '@?',
        },
        templateUrl: 'utils/directives/postpone.html',
        controller: PostponeController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

PostponeController.$inject = ['$compile', '$injector', '$scope', '$state', '$templateCache', '$timeout', 'HLResource', 'HLUtils'];
function PostponeController($compile, $injector, $scope, $state, $templateCache, $timeout, HLResource, HLUtils) {
    const vm = this;

    vm.datepickerOptions = {
        startingDay: 1, // day 1 is Monday
    };

    vm.disabledDates = disabledDates;
    vm.postponeWithDays = postponeWithDays;
    vm.getFutureDate = getFutureDate;
    vm.openPostponeModal = openPostponeModal;

    activate();

    ////

    function activate() {
        if (vm.object[vm.dateField]) {
            vm.date = moment(vm.object[vm.dateField]);
        } else {
            vm.date = moment();
        }

        vm.date = vm.date.toDate();

        _watchCloseDatePicker();

        if (!vm.showIcon) {
            vm.showIcon = true;
        }
    }

    /**
     * When the datepicker popup is closed, update model and close modal.
     *
     * @private
     */
    function _watchCloseDatePicker() {
        $scope.$watch('vm.pickerIsOpen', (newValue, oldValue) => {
            // Don't close the whole modal if we didn't change anything.
            if (!moment(vm.date).isSame(moment(vm.object[vm.dateField]))) {
                if (!newValue && oldValue) {
                    _updateDayAndCloseModal();
                }
            }
        });
    }

    function _updateDayAndCloseModal() {
        if (!moment(vm.date).isSame(moment(vm.object[vm.dateField]))) {
            // Update the due date for this case.
            const newDate = moment(vm.date).format('YYYY-MM-DD');

            const args = {
                id: vm.object.id,
            };

            args[vm.dateField] = newDate;
            // Update the model so changes are reflected instantly.
            vm.object[vm.dateField] = newDate;

            // Dynamically get the model that should be updated.
            HLResource.patch(vm.type, args).$promise.then(() => {
                swal.close();
                _processClose();
            });
        } else {
            swal.close();
            _processClose();
        }
    }

    function _processClose() {
        if (vm.callback) {
            vm.callback();
        } else {
            $state.go($state.current, {}, {reload: true});
        }
    }

    function disabledDates(currentDate, mode) {
        const date = moment.isMoment(currentDate) ? currentDate : moment(currentDate);

        // Disable Saturday and Sunday.
        return ( mode === 'day' && ( date.day() === 6 || date.day() === 0 ) );
    }

    function postponeWithDays(days) {
        vm.date = getFutureDate(days);


        // Set timeout to wait for next digest cycle before being able to set
        // the date correctly.
        $timeout(() => {
            _updateDayAndCloseModal();
        });
    }

    function getFutureDate(days) {
        let daysToAdd;

        let futureDate = moment();

        if (days) {
            daysToAdd = days;

            if (futureDate.isBefore(vm.date)) {
                futureDate = moment(vm.date);
            }
        } else {
            // The date should be the current date.
            daysToAdd = 0;
        }

        futureDate = HLUtils.addBusinessDays(daysToAdd, futureDate);

        return futureDate;
    }

    function openPostponeModal() {
        // Google Analytics events per page to track where users use the
        // postpone functionality.
        if ($state.current.name === 'base.dashboard') {
            ga('send', 'event', vm.type, 'Open postpone modal', 'Dashboard');
        }

        if ($state.current.name === 'base.cases.detail') {
            ga('send', 'event', 'Case', 'Open postpone modal', 'Case detail');
        }

        if ($state.current.name === 'base.cases') {
            ga('send', 'event', 'Case', 'Open postpone modal', 'Cases list view');
        }

        if ($state.current.name === 'base.deals.detail') {
            ga('send', 'event', 'Deal', 'Open postpone modal', 'Deal detail');
        }

        if ($state.current.name === 'base.deals') {
            ga('send', 'event', 'Deal', 'Open postpone modal', 'Deal list view');
        }

        if ($state.current.name === 'base.accounts.detail') {
            ga('send', 'event', vm.type, 'Open postpone modal', 'Account detail');
        }

        if ($state.current.name === 'base.contacts.detail') {
            ga('send', 'event', vm.type, 'Open postpone modal', 'Contact detail');
        }

        vm.bodyText = messages.alerts.postpone[vm.type.toLowerCase()];

        swal({
            title: messages.alerts.postpone[vm.type.toLowerCase() + 'Title'],
            html: $compile($templateCache.get('utils/controllers/postpone.html'))($scope),
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: 'Postpone',
        }).then(isConfirm => {
            if (isConfirm) {
                _updateDayAndCloseModal();
            }
        }).done();
    }
}
