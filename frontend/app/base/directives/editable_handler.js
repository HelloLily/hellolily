angular.module('app.directives').directive('editableHandler', editableHandler);

function editableHandler() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var form;

            if (scope.hasOwnProperty('$form')) {
                form = scope.$form;
            } else {
                form = scope[attrs.eForm];
            }

            element.on('click', function(event) {
                // For most inline editable elements the clickable area belongs to the element.
                // So check if the clicked part was actually the edit icon.
                if (event.offsetX > event.currentTarget.offsetWidth) {
                    form.$show();

                    scope.$apply();
                }
            });

            element.on('click', '.hl-edit-icon', function(event) {
                // Certain inline editable elements have a separate button,
                // so an extra check for the clicked area isn't needed.
                form.$show();

                scope.$apply();
            });
        },
    };
}
