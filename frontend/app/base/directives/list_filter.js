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
    vm.filterDisplayName = vm.filterLabel;

    $timeout(activate);

    /////

    function activate() {
        if (vm.viewModel.storedFilterList) {
            vm.viewModel.filterList = vm.viewModel.storedFilterList;

            updateFilterQuery();
            updateFilterDisplayName();
        }
    }

    function toggleFilter(filter) {
        // ngModel on a checkbox seems to load really slow, so doing the toggling this way.
        filter.selected = !filter.selected;

        updateFilterQuery();
        updateFilterDisplayName();
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
