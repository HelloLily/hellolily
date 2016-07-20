angular.module('app.utils.directives').directive('date', dateDirective);

function dateDirective() {
    return {
        restrict: 'E',
        scope: {
            date: '=',
            showTime: '=',
            addTime: '=',
            dateFormat: '@',
        },
        templateUrl: 'utils/directives/date.html',
        controller: DateController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

DateController.$inject = [];
function DateController() {
    var vm = this;
    var date;

    if (vm.date) {
        // new Date() to prevent deprecation warning of MomentJS.
        date = moment(new Date(vm.date));

        if (!vm.dateFormat) {
            if (date.isSame(moment(), 'day') && vm.showTime) {
                // In certain cases we want to display the time if it's the same day.
                vm.dateFormat = 'HH:mm';
            } else {
                if (vm.addTime) {
                    vm.dateFormat = 'dd MMM. yyyy - HH:mm'; // Renders as 29 Dec. - 2015 12:15
                } else {
                    vm.dateFormat = 'dd MMM. yyyy'; // Renders as 29 Dec. 2015
                }
            }
        } else {
            // Setting format to date to correctly use in the historylist.
            vm.date = date.format();
        }
    }
}
