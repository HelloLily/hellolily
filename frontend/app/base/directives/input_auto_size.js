angular.module('app.directives').directive('inputAutoSize', inputAutoSize);

function inputAutoSize() {
    return {
        restrict: 'A',
        link: (scope, element, attrs) => {
            scope.$watch('$data', function(newValue) {
                const minWidth = 5;
                let input = angular.element('[name="' + attrs.eName + '"]');
                let newSize = newValue.length;

                if (newSize < minWidth) {
                    // Minimum width so the input doesn't get too small.
                    newSize = minWidth;
                }

                // +1 so the input looks a bit cleaner.
                newSize += 1;

                // Set the size attribute of the input so it gets scaled.
                input.attr('size', newSize);
            });
        },
    };
}
