angular.module('app.utils.directives').directive('dueDateFilter', dueDateFilter);

function dueDateFilter() {
    return {
        restrict: 'E',
        scope: {
            filterStore: '=',
            filterField: '=',
            type: '=',
        },
        templateUrl: 'utils/directives/due_date_filter.html',
        controller: DueDateFilterWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

DueDateFilterWidgetController.$inject = ['LocalStorage', '$scope'];
function DueDateFilterWidgetController(LocalStorage, $scope) {
    var vm = this;
    var storage = LocalStorage(vm.type);

    // Get the stored value or set to 'All' if it doesn't exist
    vm.dueDateFilter = storage.get('dueDateFilter', 0);
    vm.openDueDateFilter = openDueDateFilter;

    activate();

    ////////////

    function activate() {
        _watchDueDateFilter();
    }

    // Open Due Date Filter for right element. This function gets used
    // when the breakpoints are > tablet.
    function openDueDateFilter($event) {
        angular.element($event.srcElement).next().toggleClass('is-open');
    }

    function _watchDueDateFilter() {
        $scope.$watch('vm.dueDateFilter', function() {
            var filter = '';
            var filterField = vm.filterField ? vm.filterField : 'expires';
            filterField += ': ';

            // Find element with .is-open class to close when clicking a filter.
            angular.element('.due-date-filter-container.is-open').removeClass('is-open');

            switch (vm.dueDateFilter) {
                case 0:
                    filter = '';
                    break;
                case 1:
                    var today = moment().format('YYYY-MM-DD');
                    filter = filterField + today;
                    break;
                case 2:
                    var tomorrow = moment().add(1, 'd').format('YYYY-MM-DD');
                    filter = filterField + tomorrow;
                    break;
                case 3:
                    var today = moment().format('YYYY-MM-DD');
                    var week = moment().add(6, 'd').format('YYYY-MM-DD');
                    filter = filterField + '[' + today + ' TO ' + week + ']';
                    break;
                case 4:
                    filter = filterField + '[* TO ' + moment().subtract(1, 'd').format('YYYY-MM-DD') + ']';
                    break;
            }

            storage.put('dueDateFilter', vm.dueDateFilter);
            vm.filterStore = filter;
        });
    }
}
