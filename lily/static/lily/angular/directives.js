/**
 * lilyDirectives is a container for all global lily related Angular directives
 */
angular.module('lilyDirectives', [
    'template/directive/checkbox.html'
])

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
    .directive('sortColumn', function() {

        var classes = {
            unsorted: 'sorting',
            ascending: 'sorting_asc',
            descending: 'sorting_desc'
        };

        /**
         * addClasses() removes current sorting classes and adds new based on current
         * sorting column and direction
         * @param $scope object: current scope
         * @param element object: current DOM element
         * @param sortColumn string: column from current DOM element
         */
        var setClasses = function($scope, element, sortColumn) {
            // Remove current classes
            for (var prop in classes) {
                element.removeClass(classes[prop]);
            }

            // Add classes based on current sorted column
            if($scope.table.order.column === sortColumn) {
                if ($scope.table.order.ascending) {
                    element.addClass(classes.ascending);
                } else {
                    element.addClass(classes.descending);
                }
            } else {
                element.addClass(classes.unsorted);
            }
        };

        return {
            restrict: 'A',
            scope: {
                table: '='
            },
            link: function ($scope, element, attrs) {
                // Watch the table ordering & sorting
                $scope.$watchCollection('table.order', function() {
                    setClasses($scope, element, attrs.sortColumn);
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
    })

    /**
     * checkbox Directive makes a nice uniform checkbox and binds to a model
     *
     * @param model object: model to bind checkbox with
     *
     * Example:
     *
     * <checkbox model="table.visibility.name">Name</checkbox>
     */
    .directive('checkbox', function() {
        return {
            restrict: 'E',
            replace: true,
            transclude: true,
            scope: {
                model: '='
            },
            templateUrl: 'template/directive/checkbox.html'
        }
    });

/**
 * Template for checkbox directive
 */
angular.module('template/directive/checkbox.html', [])
    .run(['$templateCache', function($templateCache) {
        $templateCache.put('template/directive/checkbox.html',
                '<label>' +
                    '<div class="checker">' +
                        '<span ng-class="{checked: model}">' +
                            '<input type="checkbox" data-skip-uniform ng-model="model">' +
                        '</span>' +
                    '</div> ' +
                    '<ng-transclude></ng-transclude>' +
                '</label>');
    }]
);
