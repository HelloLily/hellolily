(function() {
    'use strict';

    /**
     * app.directives is a container for all global lily related Angular directives
     */
    angular.module('app.directives', []);

    angular.module('app.directives').directive('ngSpinnerBar', ngSpinnerBar);

    ngSpinnerBar.$inject = ['$rootScope'];
    function ngSpinnerBar ($rootScope) {
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
            templateUrl: 'directives/sorting.html',
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

    /**
     * checkbox Directive makes a nice uniform checkbox and binds to a model
     *
     * @param model object: model to bind checkbox with
     *
     * Example:
     *
     * <checkbox model="table.visibility.name">Name</checkbox>
     */
    angular.module('app.directives').directive('checkbox', checkbox);

    function checkbox () {
        return {
            restrict: 'E',
            replace: true,
            transclude: true,
            scope: {
                model: '='
            },
            templateUrl: 'directives/checkbox.html'
        }
    }

    /**
     *
     */
    angular.module('app.directives').directive('resizeIframe', resizeIframe);

    function resizeIframe () {
        return {
            restrict: 'A',
            link: function ($scope, element, attrs) {
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
    }

    /**
     * Directive used for the save and archive button. It checks the current
     * state of the hidden field and changes it accordingly and submits
     * the form
     */
    angular.module('app.directives').directive('saveAndArchive', saveAndArchive);

    function saveAndArchive () {
        return {
            restrict: 'A',
            link: function(scope, elem, attrs) {

                // Setting button to right text based in archived state
                var $button = $('#archive-button'),
                    $archiveField = $('#id_is_archived');
                if ($archiveField.val() === 'True') {
                    $button.find('span').text('Save and Unarchive');
                } else {
                    $button.find('span').text('Save and Archive');
                }

                // On button click set archived hidden field and submit form
                $(elem).click(function() {
                    $button = $('#archive-button');
                    $archiveField = $('#id_is_archived');
                    var $form = $($button.closest('form').get(0)),
                        archive = ($archiveField.val() === 'True' ? 'False' : 'True');
                    $archiveField.val(archive);
                    $button.button('loading');
                    $form.find(':submit').click();
                    event.preventDefault();
                });
            }
        }
    }

    /**
     * Directive for a confirmation box before the delete in the detail
     * view happens
     */
    angular.module('app.directives').directive('detailDelete', detailDelete);

    detailDelete.$inject = ['$state'];
    function detailDelete ($state) {
        return {
            restrict: 'A',
            link: function (scope, elem, attrs) {

                $(elem).click(function () {
                    if (confirm('You are deleting! Are you sure ?')) {
                        $state.go('.delete');
                    }
                });
            }
        }
    }

    /**
     * Directive give a nice formatting on input elements.
     *
     * It makes sure that the value of the ngModel on the scope has a nice
     * formatting for the user
     */
    angular.module('app.directives').directive('dateFormatter', dateFormatter);

    dateFormatter.$inject = ['dateFilter'];
    function dateFormatter(dateFilter) {
        return {
            restrict: 'A',
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                ngModel.$formatters.push(function(value) {
                    if (value) {
                        return dateFilter(value, attrs.dateFormatter);
                    }
                })
            }
        }
    }
})();
