angular.module('app.services').service('HLFilters', HLFilters);

function HLFilters() {
    this.updateFilterQuery = function(viewModel) {
        viewModel.table.filterQuery = '';
        viewModel.displayFilterClear = false;
        var filterStrings = [];

        for (var i = 0; i < viewModel.filterList.length; i++) {
            var filter = viewModel.filterList[i];
            if (filter.id && filter.id === 'archived') {
                if (!filter.selected) {
                    filterStrings.push('archived:false');
                } else {
                    viewModel.displayFilterClear = true;
                }
            } else {
                if (filter.selected) {
                    filterStrings.push(filter.value);
                    viewModel.displayFilterClear = true;
                }
            }
        }

        if (viewModel.table.dueDateFilter) {
            filterStrings.push(viewModel.table.dueDateFilter);
        }

        viewModel.table.filterQuery = filterStrings.join(' AND ');
    };

    this.clearFilters = function(viewModel) {
        for (var i = 0; i < viewModel.filterList.length; i++) {
            viewModel.filterList[i].selected = false;
        }

        viewModel.updateFilterQuery();
    };
}
