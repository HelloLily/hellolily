angular.module('app.utils.directives').directive('date', dateDirective);

function dateDirective() {
    return {
        restrict: 'E',
        scope: {
            date: '=',
            showTime: '=',
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

    if (vm.date) {
        var date = moment(vm.date);

        if (date.isSame(moment(), 'day') && vm.showTime) {
            // In certain cases we want to display the time if it's the same day.
            vm.dateFormat = 'HH:mm';
        } else {
            vm.dateFormat = 'dd MMM. yyyy'; // Renders as 29 Dec. 2015
        }
    }
}
