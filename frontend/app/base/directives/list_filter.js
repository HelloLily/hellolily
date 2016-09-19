angular.module('app.directives').directive('listFilter', listFilter);

function listFilter() {
    return {
        restrict: 'E',
        scope: {
            filterLabel: '=',
            filterLabelPlural: '=',
            viewModel: '=',
        },
        templateUrl: 'base/directives/list_filter.html',
        controller: ListFilterController,
        controllerAs: 'vm',
        bindToController: true,
    };
}

ListFilterController.$inject = ['$filter', '$timeout', 'HLFilters'];
function ListFilterController($filter, $timeout, HLFilters) {
    var vm = this;

    vm.toggleFilter = toggleFilter;
    vm.setAll = setAll;
    vm.updateFilterQuery = updateFilterQuery;

    vm.allSelected = false;
    vm.filterDisplayName = vm.filterLabel;
    vm.filterPlural = vm.filterLabelPlural;

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

    function setAll(value) {
        var newValue;

        var filterList = vm.viewModel.filterList;

        if (vm.viewModel.filterSpecialList) {
            filterList = vm.viewModel.filterSpecialList;
        }

        if (typeof value !== 'undefined') {
            // Set all items to the given value.
            newValue = value;
        } else {
            // Deselect/Select all items.
            vm.allSelected = !vm.allSelected;
            newValue = vm.allSelected;
        }

        angular.forEach(filterList, function(item) {
            item.selected = newValue;
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

        if (vm.viewModel.hasOwnProperty('updateTable')) {
            vm.viewModel.updateTable();
        }

        vm.viewModel.storage.put('filterListSelected', vm.viewModel.filterList);
        vm.viewModel.storage.put('filterSpecialListSelected', vm.viewModel.filterSpecialList);
    }

    function updateFilterDisplayName() {
        var filterList = vm.viewModel.filterList;
        var selectedItems = [];
        var label = vm.filterLabel;

        if (vm.viewModel.filterSpecialList) {
            filterList = vm.viewModel.filterSpecialList;
        }

        selectedItems = $filter('filter')(filterList, {selected: true});

        if (selectedItems.length) {
            if (selectedItems.length < 3) {
                label = selectedItems.map(function(item) {
                    return item.name;
                }).join(' + ');
            } else {
                label = selectedItems.length + ' ' + vm.filterLabel + ' selected';
            }

            vm.displayClearButton = true;
        } else {
            vm.displayClearButton = false;
        }

        vm.filterDisplayName = label;
    }
}
