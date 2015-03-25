/**
 * lilyDirectives is a container for all global lily related Angular directives
 */
var lilyDirectives = angular.module('lilyDirectives', [
    'template/directive/checkbox.html'
]);

lilyDirectives.directive('ngSpinnerBar', ['$rootScope',
    function($rootScope) {
        return {
            link: function(scope, element, attrs) {
                // by defult hide the spinner bar
                element.addClass('hide'); // hide spinner bar by default

                // display the spinner bar whenever the route changes(the content part started loading)
                $rootScope.$on('$stateChangeStart', function() {
                    element.removeClass('hide'); // show spinner bar
                });

                // hide the spinner bar on rounte change success(after the content loaded)
                $rootScope.$on('$stateChangeSuccess', function() {
                    element.addClass('hide'); // hide spinner bar
                    $('body').removeClass('page-on-load'); // remove page loading indicator
                    Layout.setSidebarMenuActiveLink('match'); // activate selected link in the sidebar menu

                    // auto scroll to page top
                    setTimeout(function () {
                        Metronic.scrollTop(); // scroll to the top on content load
                    }, $rootScope.settings.layout.pageAutoScrollOnLoad);
                });

                // handle errors
                $rootScope.$on('$stateNotFound', function() {
                    element.addClass('hide'); // hide spinner bar
                });

                // handle errors
                $rootScope.$on('$stateChangeError', function() {
                    element.addClass('hide'); // hide spinner bar
                });
            }
        };
    }
]);

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
lilyDirectives.directive('sortColumn', function() {
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
});

/**
 * checkbox Directive makes a nice uniform checkbox and binds to a model
 *
 * @param model object: model to bind checkbox with
 *
 * Example:
 *
 * <checkbox model="table.visibility.name">Name</checkbox>
 */
lilyDirectives.directive('checkbox', function() {
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
 *
 */
lilyDirectives.directive('resizeIframe', function() {
    return {
        restrict: 'A',
        link: function ($scope, element, attrs ) {
            var maxHeight = $('body').outerHeight();
            element.on('load', function() {
                element.removeClass('hidden');

                // do this after .inbox-view is visible
                var ifDoc, ifRef = this;

                // set ifDoc to 'document' from frame
                try {
                    ifDoc = ifRef.contentWindow.document.documentElement;
                } catch (e1) {
                    try {
                        ifDoc = ifRef.contentDocument.documentElement;
                    } catch (e2) {
                    }
                }

                // calculate and set max height for frame
                if (ifDoc) {
                    var subtractHeights = [
                        element.offset().top,
                        $('.footer').outerHeight(),
                        $('.inbox-attached').outerHeight()
                    ];
                    for (var height in subtractHeights) {
                        maxHeight = maxHeight - height;
                    }

                    if (ifDoc.scrollHeight > maxHeight) {
                        ifRef.height = maxHeight;
                    } else {
                        ifRef.height = ifDoc.scrollHeight;
                    }
                }
            });
        }
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
