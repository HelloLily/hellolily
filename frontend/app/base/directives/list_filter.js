angular.module('app.directives').directive('listFilter', listFilter);

function listFilter() {
    return {
        restrict: 'E',
        scope: {
            filterLabel: '=',
            viewModel: '=',
        },
        templateUrl: 'base/directives/list_filter.html',
        controller: ListFilterController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

ListFilterController.$inject = ['$timeout', 'HLFilters'];
function ListFilterController($timeout, HLFilters) {
    var vm = this;

    vm.toggleFilter = toggleFilter;
    vm.updateFilterQuery = updateFilterQuery;

    $timeout(activate);

    /////

    function activate() {
        if (vm.viewModel.storedFilterList) {
            vm.viewModel.filterList = vm.viewModel.storedFilterList;

            updateFilterQuery();
        }
    }

    function toggleFilter(filter) {
        // ngModel on a checkbox seems to load really slow, so doing the toggling this way.
        filter.selected = !filter.selected;

        updateFilterQuery();
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm.viewModel);

        vm.viewModel.updateTable();

        vm.viewModel.storage.put('filterListSelected', vm.viewModel.filterList);
    }
}
