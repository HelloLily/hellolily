angular.module('app.services').service('HLFilters', HLFilters);

function HLFilters() {
    this.updateFilterQuery = function(viewModel, hasClearButtons) {
        // Update the filter based on the separate filters.
        var filterStrings = [];
        var specialFilterStrings = [];

        viewModel.table.filterQuery = '';

        if (hasClearButtons) {
            this._displayClearButtons(viewModel);
        }

        viewModel.filterList.forEach(function(filter) {
            if (filter.id && filter.id === 'archived') {
                if (!filter.selected) {
                    filterStrings.push('archived:false');
                }
            } else {
                if (filter.selected) {
                    if (filter.isSpecialFilter) {
                        specialFilterStrings.push(filter.value);
                    } else {
                        filterStrings.push(filter.value);
                    }
                }
            }
        });

        if (viewModel.table.dueDateFilter) {
            filterStrings.push(viewModel.table.dueDateFilter);
        }

        // If we have type filter, we join them OR-wise.
        if (specialFilterStrings.length > 0) {
            filterStrings.push('(' + specialFilterStrings.join(' OR ') + ')');
        }

        if (viewModel.table.usersFilter) {
            filterStrings.push('(' + viewModel.table.usersFilter + ')');
        }

        // Finally join all filters AND-wise.
        viewModel.table.filterQuery = filterStrings.join(' AND ');
    };

    this._displayClearButtons = function(viewModel) {
        viewModel.displayFilterClear = false;
        viewModel.displaySpecialFilterClear = false;

        viewModel.filterList.forEach(function(filter) {
            if (filter.selected) {
                if (filter.isSpecialFilter) {
                    viewModel.displaySpecialFilterClear = true;
                } else {
                    viewModel.displayFilterClear = true;
                }
            }
        });
    };

    this.clearFilters = function(viewModel, clearSpecial) {
        for (var i = 0; i < viewModel.filterList.length; i++) {
            if (clearSpecial) {
                if (viewModel.filterList[i].isSpecialFilter) {
                    // Clear special filters.
                    viewModel.filterList[i].selected = false;
                }
            } else {
                // Otherwise clear the standard filters.
                viewModel.filterList[i].selected = false;
            }
        }

        viewModel.updateFilterQuery();
    };

    this.getStoredSelections = function(filterList, storedFilterList) {
        if (storedFilterList) {
            // Stored filter list exists, merge the selections from with the stored values.
            angular.forEach(storedFilterList, function(storedFilter) {
                angular.forEach(filterList, function(filter) {
                    if (storedFilter.name === filter.name) {
                        filter.selected = storedFilter.selected;
                    }
                });
            });
        }
    };
}
