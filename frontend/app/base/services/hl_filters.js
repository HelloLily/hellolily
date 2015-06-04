angular.module('app.services').service('HLFilters', HLFilters);

function HLFilters () {
    this.updateFilterQuery = function ($scope) {
        $scope.table.filterQuery = '';
        $scope.displayFilterClear = false;
        var filterStrings = [];

        for (var i = 0; i < $scope.filterList.length; i++) {
            var filter = $scope.filterList[i];
            if (filter.id && filter.id == 'archived') {
                if (!filter.selected) {
                    filterStrings.push('archived:false');
                }
                else {
                    $scope.displayFilterClear = true;
                }
            }
            else {
                if (filter.selected) {
                    filterStrings.push(filter.value);
                    $scope.displayFilterClear = true;
                }
            }
        }

        $scope.table.filterQuery = filterStrings.join(' AND ');
    };

    this.clearFilters = function ($scope) {
        for (var i = 0; i < $scope.filterList.length; i++) {
            $scope.filterList[i].selected = false;
        }

        $scope.updateFilterQuery();
    };
}
