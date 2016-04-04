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
    vm.toggleAll = toggleAll;
    vm.updateFilterQuery = updateFilterQuery;
    vm.allSelected = false;
    vm.filterDisplayName = vm.filterLabel;

    $timeout(activate);

    /////

    function activate() {
        var update = false;
        if (vm.viewModel.storedFilterList) {
            vm.viewModel.filterList = vm.viewModel.storedFilterList;
            update = true;
        }

        if (vm.viewModel.storedFilterSpecialList) {
            vm.viewModel.filterSpecialList = vm.viewModel.storedFilterSpecialList;
            update = true;
        }

        if (update) {
            updateAllSelected();
            updateFilterQuery();
            updateFilterDisplayName();
        }
    }

    function toggleAll() {
        var filterList = vm.viewModel.filterList;
        if (vm.viewModel.filterSpecialList) {
            filterList = vm.viewModel.filterSpecialList;
        }
        vm.allSelected = !vm.allSelected;

        // Deselect/Select all items.
        angular.forEach(filterList, function(item) {
            item.selected = vm.allSelected;
        });

        updateFilterQuery();
        updateFilterDisplayName();
    }

    function toggleFilter(filter) {
        // ngModel on a checkbox seems to load really slow, so doing the toggling this way.
        filter.selected = !filter.selected;

        updateAllSelected();
        updateFilterQuery();
        updateFilterDisplayName();
    }

    function updateAllSelected() {
        // Keep the All selected checkbox in sync whether or not all items are selected.
        var filterList = vm.viewModel.filterList;
        if (vm.viewModel.filterSpecialList) {
            filterList = vm.viewModel.filterSpecialList;
        }
        vm.allSelected = true;
        angular.forEach(filterList, function(item) {
            if (!item.selected) {
                vm.allSelected = false;
            }
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm.viewModel);

        vm.viewModel.updateTable();

        vm.viewModel.storage.put('filterListSelected', vm.viewModel.filterList);
        vm.viewModel.storage.put('filterSpecialListSelected', vm.viewModel.filterSpecialList);
    }

    function updateFilterDisplayName() {
        var count = 0;
        var filterList = vm.viewModel.filterList;
        if (vm.viewModel.filterSpecialList) {
            filterList = vm.viewModel.filterSpecialList;
        }
        vm.filterDisplayName = vm.filterLabel;

        angular.forEach(filterList, function(item) {
            if (item.selected === true) {
                count += 1;
                if (count === 1) {
                    vm.filterDisplayName = item.name + ' selected';
                } else if (count > 1) {
                    vm.filterDisplayName = count + ' Types selected';
                }
            }
        });
    }
}
