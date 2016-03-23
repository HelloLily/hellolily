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
        if (vm.viewModel.storedFilterList) {
            vm.viewModel.filterList = vm.viewModel.storedFilterList;

            updateAllSelected();
            updateFilterQuery();
            updateFilterDisplayName();
        }
    }

    function toggleAll() {
        vm.allSelected = !vm.allSelected;

        // Deselect / Select all items
        angular.forEach(vm.viewModel.filterList, function(item) {
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
        // Keep the All selected checkbox in sync whether or not all items are selected
        vm.allSelected = true;
        angular.forEach(vm.viewModel.filterList, function(item) {
            if(!item.selected){
                vm.allSelected = false;
            }
        });
    }

    function updateFilterQuery() {
        HLFilters.updateFilterQuery(vm.viewModel);

        vm.viewModel.updateTable();

        vm.viewModel.storage.put('filterListSelected', vm.viewModel.filterList);
    }

    function updateFilterDisplayName() {
        var count = 0;
        vm.filterDisplayName = vm.filterLabel;
        angular.forEach(vm.viewModel.filterList, function(item){
            if(item.selected === true) {
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
