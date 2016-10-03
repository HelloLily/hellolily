angular.module('app.directives').directive('inputAutoSize', inputAutoSize);

function inputAutoSize() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            scope.$watch('$data', function(newValue) {
                var input = angular.element('[name="' + attrs.eName + '"]');

                // Set the size attribute of the input so it gets scaled.
                input.attr('size', newValue.length);
            });
        },
    };
}
