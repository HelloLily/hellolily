/**
 * sortColumn Directive adds sorting classes to an DOM element based on `table` object
 *
 * It makes the element clickable and sets the table sorting based on that element
 *
 * @param sortColumn string: name of the column to sort on when clicked
 * @param table object: The object to bind sort column and ordering
 *
 * Example:
 *
 * <th sort-column="last_name" table="table">Name</th>
 *
 * Possible classes:
 * - sorting: Unsorted
 * - sorting_asc: Sorted ascending
 * - sorting_desc: Sorted descending
 */
angular.module('app.directives').directive('sortColumn', sortColumn);

function sortColumn () {
    /**
     * _setSortableIcon() removes current sorting classes and adds new based on current
     * sorting column and direction
     *
     * @param $scope object: current scope
     * @param element object: current DOM element
     * @param sortColumn string: column from current DOM element
     */
    var _setSortableIcon = function($scope, element, sortColumn) {
        // Add classes based on current sorted column
        if($scope.table.order.column === sortColumn) {
            if ($scope.table.order.ascending) {
                $scope.sorted = 1;
            } else {
                $scope.sorted = -1;
            }
        } else {
            $scope.sorted = 0;
        }
    };

    return {
        restrict: 'A',
        scope: {
            table: '='
        },
        transclude: true,
        templateUrl: 'base/directives/sort_column.html',
        link: function ($scope, element, attrs) {
            // Watch the table ordering & sorting
            $scope.$watchCollection('table.order', function() {
                _setSortableIcon($scope, element, attrs.sortColumn);
            });

            // When element is clicked, set the table ordering & sorting based on this DOM element
            element.on('click', function() {
                if($scope.table.order.column === attrs.sortColumn) {
                    $scope.table.order.ascending = !$scope.table.order.ascending;
                    $scope.$apply();
                } else {
                    $scope.table.order.column = attrs.sortColumn;
                    $scope.$apply();
                }
            });
        }
    }
}
