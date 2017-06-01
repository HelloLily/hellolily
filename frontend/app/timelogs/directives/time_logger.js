let Duration = require('duration-js');

angular.module('app.timelogs.directives').directive('timeLogger', timeLogger);

function timeLogger() {
    return {
        restrict: 'E',
        scope: {
            object: '=',
            updateCallback: '&?',
            small: '@?',
            timeLog: '=?',
        },
        templateUrl: 'timelogs/directives/time_logger.html',
        controller: TimeLoggerController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

TimeLoggerController.$inject = ['$compile', '$scope', '$state', '$templateCache', 'TimeLog'];
function TimeLoggerController($compile, $scope, $state, $templateCache, TimeLog) {
    const vm = this;
    const MONDAY = 1;

    vm.currentUser = currentUser;
    vm.datepickerOptions = {
        startingDay: MONDAY,
    };
    vm.error = false;

    const isEdit = typeof vm.timeLog !== 'undefined';

    let gfkContentType;
    let gfkObjectId;

    if (!isEdit) {
        gfkContentType = vm.object.content_type;

        if (typeof vm.object.content_type === 'object') {
            gfkContentType = vm.object.content_type.id;
        }

        gfkObjectId = vm.object.id;
    } else {
        gfkContentType = vm.timeLog.gfk_content_type;
        gfkObjectId = vm.timeLog.gfk_object_id;

        vm.timeLog.date = moment(vm.timeLog.date).toDate();
        // We use a different property so we can keep the front end clean when formatting the time.
        vm.timeLog.time = vm.timeLog.hours_logged;
    }

    const timeLogDefaults = {
        gfk_content_type: gfkContentType,
        gfk_object_id: gfkObjectId,
        date: moment().toDate(),
        billable: currentUser.timeLogging.billingDefault,
        content: '',
    };

    if (!isEdit) {
        vm.timeLog = Object.assign({}, timeLogDefaults);
    }

    vm.logTime = logTime;
    vm.formatTime = formatTime;
    vm.openTimeLogModal = openTimeLogModal;

    vm.users = {};

    if (!isEdit) {
        vm.object.timeLogs.forEach(timeLog => {
            const {user} = timeLog;

            // Add the user to the list if it isn't already in there.
            if (!vm.users.hasOwnProperty(user.id)) {
                const {id, full_name, profile_picture} = user;

                vm.users[user.id] = {
                    id,
                    full_name,
                    profile_picture,
                    timeLogs: [],
                };
            }

            vm.users[user.id].timeLogs.push(timeLog);
        });

        // Checking the length with Object.keys doesn't seem to work in the template.
        vm.hasCollaborators = Object.keys(vm.users).length > 0;
    }

    function logTime() {
        vm.error = false;
        const hoursLogged = formatTime();

        if (hoursLogged) {
            vm.timeLog.hours_logged = hoursLogged;

            let promise;

            if (isEdit) {
                promise = TimeLog.patch(vm.timeLog).$promise;
            } else {
                promise = TimeLog.save(vm.timeLog).$promise;
            }

            promise.then(response => {
                toastr.success('Your hours have been logged', 'Done!');
                $state.reload();
            }, response => {
                toastr.error('Uh oh, there seems to be a problem', 'Oops!');
            });
        } else {
            toastr.error('Uh oh, there seems to be a problem', 'Oops!');
            vm.error = true;
        }
    }

    function formatTime() {
        let time = vm.timeLog.time;
        vm.error = false;

        // No number in the given time, so invalid input.
        if (!/[0-9]/i.test(time)) {
            time = null;
        }

        if (time) {
            // The parser library only accepts the shorthand notation, so replace full words.
            time = time.replace('hour', 'h');
            time = time.replace('min', 'm');
            // No unit given so resort to default (hours).
            if (!/[a-z]/i.test(time)) {
                time += 'h';
            }

            time = time.replace(',', '.');

            try {
                time = new Duration(time);
            } catch (e) {
                // Invalid unit given, so incorrect input.
                time = null;
                vm.error = true;
            }

            if (time) {
                time = (time.minutes() / 60).toFixed(3);
            }
        } else {
            vm.error = true;
        }

        return time;
    }

    function openTimeLogModal() {
        if (vm.timeLog.time) {
            const time = parseFloat(vm.timeLog.time);
            let hours = Math.floor(time);
            hours = hours ? `${hours}h ` : '';
            let minutes = Math.round(time % 1 * 60);
            minutes = minutes ? `${minutes}m` : '';

            // Convert back to human readable.
            vm.timeLog.time = `${hours}${minutes}`;
        }

        swal({
            title: messages.alerts.timeLog.modalTitle,
            html: $compile($templateCache.get('timelogs/controllers/time_logger.html'))($scope),
            showCloseButton: true,
            showCancelButton: true,
            confirmButtonText: messages.alerts.timeLog.confirmButtonText,
        }).then(isConfirm => {
            // For some reason the datepicker doesn't get removed from the DOM when the SweetAlert is closed.
            // So just hide the datepicker as soon as the modal closes.
            const element = angular.element($('[uib-datepicker-popup-wrap]'));
            element.hide();

            if (isConfirm) {
                logTime();
            }
        }).done();
    }
}
