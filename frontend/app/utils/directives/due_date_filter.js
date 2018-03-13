angular.module('app.utils.directives').directive('dueDateFilter', dueDateFilter);

function dueDateFilter() {
    return {
        restrict: 'E',
        scope: {
            filterStore: '=',
            filterField: '@',
            type: '=',
        },
        templateUrl: 'utils/directives/due_date_filter.html',
        controller: DueDateFilterWidgetController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

DueDateFilterWidgetController.$inject = ['$scope', '$state', '$timeout', 'HLFilters', 'LocalStorage'];
function DueDateFilterWidgetController($scope, $state, $timeout, HLFilters, LocalStorage) {
    const vm = this;
    const storage = new LocalStorage(vm.type);

    // Get the stored value or set to 'All' if it doesn't exist
    vm.storedFilterList = storage.get('filterListSelected', null);
    vm.openDueDateFilter = openDueDateFilter;

    $timeout(() => {
        activate();
    }, 100);

    ////////////

    function activate() {
        const filterField = vm.filterField ? vm.filterField : 'expires';

        // Use the value from storage first.
        // (Because it is faster; loading the list uses AJAX requests).
        if (vm.storedFilterList) {
            vm.filterList = vm.storedFilterList;
        }

        // But we still update the list afterwards (in case a filter was changed)
        const filterList = [
            {
                name: 'Expired',
                value: `${filterField}: [* TO ${moment().subtract(1, 'd').format('YYYY-MM-DD')}]`,
                selected: false,
            },
            {
                name: 'Today',
                value: `${filterField}: ${moment().format('YYYY-MM-DD')}`,
                selected: false,
            },
            {
                name: 'Tomorrow',
                value: `${filterField}: ${moment().add(1, 'd').format('YYYY-MM-DD')}`,
                selected: false,
            },
            {
                name: 'Next 7 days',
                value: `${filterField}: [${moment().format('YYYY-MM-DD')} TO ${moment().add(7, 'd').format('YYYY-MM-DD')}]`,
                selected: false,
            },
            {
                name: 'Later',
                value: `${filterField}: [${moment().add(7, 'd').format('YYYY-MM-DD')} TO *]`,
                selected: false,
            },
        ];

        if ($state.current.name !== 'base.dashboard') {
            filterList.unshift({
                name: 'Archived',
                value: '',
                selected: false,
            });
        }

        // Merge previous stored selection with new filters.
        HLFilters.getStoredSelections(filterList, vm.storedFilterList);

        vm.filterList = filterList;
    }

    // Open Due Date Filter for right element. This function gets used
    // when the breakpoints are > tablet.
    function openDueDateFilter($event) {
        angular.element($event.srcElement).next().toggleClass('is-open');
    }

    $scope.$watch('vm.filterList', () => {
        if (vm.filterList) {
            // Find element with .is-open class to close when clicking a filter.
            angular.element('.due-date-filter-container.is-open').removeClass('is-open');

            let filterList = [];
            let filterStore = '';

            vm.filterList.forEach(filter => {
                if (filter.name === 'Archived') {
                    if (!filter.selected) {
                        filterStore += 'is_archived:false';
                    }
                } else {
                    if (filter.selected) {
                        filterList.push(filter.value);
                    }
                }
            });

            if (filterStore && filterList.length) {
                filterStore += ' AND ';
            }

            filterStore += filterList.length ? `(${filterList.join(' OR ')})` : '';

            vm.filterStore = filterStore;

            storage.put('filterListSelected', vm.filterList);
        }
    }, true);
}
