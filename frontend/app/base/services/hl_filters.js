angular.module('app.services').service('HLFilters', HLFilters);

function HLFilters() {
    this.updateFilterQuery = (viewModel, hasClearButtons) => {
        // Update the filter based on the separate filters.
        let filterStrings = [];
        let specialFilterStrings = [];
        let separateFilterStrings = [];
        let filterList = viewModel.filterList;

        if (hasClearButtons) {
            this._displayClearButtons(viewModel);
        }

        if (viewModel.filterSpecialList) {
            filterList = filterList.concat(viewModel.filterSpecialList);
        }

        filterList.forEach(filter => {
            if (filter.id && filter.id === 'is_archived') {
                if (!filter.selected) {
                    filterStrings.push('is_archived:false');
                }
            } else if (filter.selected) {
                if (filter.isSpecialFilter) {
                    if (filter.separate) {
                        separateFilterStrings.push(filter.value);
                    } else {
                        specialFilterStrings.push(filter.value);
                    }
                } else {
                    filterStrings.push(filter.value);
                }
            }
        });

        if (viewModel.table.dueDateFilter) {
            filterStrings.push(viewModel.table.dueDateFilter);
        }

        // If we have a special filter, we join them OR-wise.
        if (specialFilterStrings.length) {
            filterStrings.push('(' + specialFilterStrings.join(' OR ') + ')');
        }

        if (separateFilterStrings.length) {
            filterStrings.push('(' + separateFilterStrings.join(' OR ') + ')');
        }

        if (viewModel.table.usersFilter) {
            filterStrings.push('(' + viewModel.table.usersFilter + ')');
        }

        // Finally join all filters AND-wise.
        viewModel.table.filterQuery = filterStrings.join(' AND ');
    };

    this._displayClearButtons = viewModel => {
        viewModel.displayFilterClear = false;
        viewModel.displaySpecialFilterClear = false;

        viewModel.filterList.forEach(filter => {
            if (filter.selected) {
                viewModel.displayFilterClear = true;
            }
        });

        if (viewModel.filterSpecialList) {
            viewModel.filterSpecialList.forEach(filter => {
                if (filter.selected) {
                    viewModel.displaySpecialFilterClear = true;
                }
            });
        }
    };

    this.clearFilters = (viewModel, clearSpecial) => {
        if (clearSpecial) {
            viewModel.filterSpecialList.forEach(filter => {
                filter.selected = false;
            });
        } else {
            viewModel.filterList.forEach(filter => {
                filter.selected = false;
            });
        }

        viewModel.updateFilterQuery();
    };

    this.getStoredSelections = (filterList, storedFilterList) => {
        if (storedFilterList) {
            // Stored filter list exists, merge the selections from with the stored values.
            storedFilterList.forEach(storedFilter => {
                filterList.forEach(filter => {
                    if (storedFilter.name === filter.name) {
                        filter.selected = storedFilter.selected;
                    }
                });
            });
        }
    };
}
