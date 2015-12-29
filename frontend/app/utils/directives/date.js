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
            if (window.innerWidth < 992) {
                // Display as a short version if it's a small screen (tablet, smartphone, etc.)
                vm.dateFormat = 'dd MMM. yyyy'; // Renders as 29 Dec. 2015
            } else {
                vm.dateFormat = 'dd MMMM yyyy'; // Renders as 29 December 2015
            }
        }
    }
}
